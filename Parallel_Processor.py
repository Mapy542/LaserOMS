import tinydb, json

import multiprocessing, datetime, threading


def checkForReprocess(database):
    """Checks the DB for a transient listing the last time the data was processed. Returns true if reprocessing is needed.

    Args:
        database (tinydb): The database to check for a transient.

    Returns:
        bool: True if reprocessing is needed.
    """

    settings = database.table("Settings")
    reprocessTime = settings.search(tinydb.Query().setting_name == "Reprocess_Frequency_Days")[0][
        "setting_value"
    ]

    transients = database.table("Transients")
    lastProcessTimeSearch = transients.search(
        tinydb.Query().transient_name == "Last_Processing_Timestamp"
    )
    if len(lastProcessTimeSearch) == 0:
        return True

    lastProcessTime = lastProcessTimeSearch[0]["processing_timestamp"]

    checkTime = (
        lastProcessTime + reprocessTime * 24 * 60 * 60
    )  # takes the last processing time and adds the reprocess frequency in seconds

    return checkTime < datetime.datetime.now().timestamp()


def serializeDB(database):
    """Serializes the database to a json string.

    Args:
        database (tinydb): The database to serialize.

    Returns:
        str: The serialized database.
    """

    return json.dumps(database.storage.read())


def deserializeDB(serializedDB):
    """Deserializes a json string into a tinydb database.

    Args:
        serializedDB (str): The serialized database.

    Returns:
        tinydb: The deserialized database.
    """

    db = tinydb.TinyDB(storage=tinydb.storages.MemoryStorage)
    db.storage.write(json.loads(serializedDB))
    return db


def pollForParallelProcessing(database, app):
    """This functions checks if parallel processing is needed to be run and starts the process if so.

    Args:
        database (tinydb): The database to check for a transient.
        app (Application): The application to log to.

    Returns:
        None
    """

    if checkForReprocess(database):
        parallelProcessInterface = threading.Thread(
            target=parallelProcessThread, args=(database, app), daemon=True
        )
        parallelProcessInterface.start()


def forceParallelProcessing(database, app):
    """Force parallel processing to run. (Avoids the transient check and returns immediately after starting the start thread)

    Args:
        database (tinydb): The database to process.
        app (Application): The application to log to.
    """

    parallelProcessInterface = threading.Thread(
        target=parallelProcessThread, args=(database, app), daemon=True
    )
    parallelProcessInterface.start()


def parallelProcessThread(database, app):
    """This function starts and interfaces the parallel processing. Should be run as a thread.
    We need direct access to the database and app, but it may take a long time to serialize the db and return job values.

    Args:
        database (tinydb): The database to process.

    Returns:
        None
    """

    settings = database.table("Settings")
    maxProcesses = settings.search(tinydb.Query().setting_name == "Max_Parallel_Processes")[0][
        "setting_value"
    ]

    try:
        maxProcesses = int(maxProcesses)
    except ValueError:
        app.error(
            "Invalid value for 'Max_Parallel_Processes' in settings. Using number value instead."
        )
        return

    jobs = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()

    dbCopy = serializeDB(database)
    [
        jobs.put(job) for job in jobClasses
    ]  # issues all jobs to the queue. This must be done before the processes are started. They exit if the queue is empty.

    parallelProcessors = [
        multiprocessing.Process(target=processJobsThread, args=(dbCopy, results, jobs), daemon=True)
        for _ in range(maxProcesses)
    ]

    [p.start() for p in parallelProcessors]

    applyResults(database, results, jobs)


def applyResults(
    database: tinydb.TinyDB,
    resultsQueue: multiprocessing.Queue,
    jobsQueue: multiprocessing.JoinableQueue,
):
    """Applies the results of the parallel processing to the database.

    Args:
        database (TinyDB): The database to apply the results to.
        resultsQueue (multiprocessing.Queue): The queue to get the results from.
        jobsQueue (multiprocessing.QueueJoinable): The queue to get the jobs from.
    """

    transients = database.table("Transients")

    while not jobsQueue.empty() and not resultsQueue.empty():
        result = resultsQueue.get()

        transients.upsert(result, tinydb.Query().transient_name == result["transient_name"])


def processJobsThread(databaseCopy, jobsQueue, resultsQueue):
    """Processes the jobs in the jobsQueue.

    Args:
        databaseCopy (TinyDB): The database to process the jobs on.
        jobsQueue (multiprocessing.QueueJoinable): The queue to get the jobs from.
        resultsQueue (multiprocessing.Queue): The queue to put the results in.
    """

    pass


class Job:
    def __init__(self, name, jobJson):
        self.name = name
        self.jobJson = jobJson

    def functionalize(self):
        """Converts the job into a function that can be run in parallel."""
