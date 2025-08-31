import datetime
import json
import multiprocessing
import threading

import tinydb

import Parallel_Jobs

BACKGROUND_COMMON_JOBS = [
    Parallel_Jobs.RevenueCalculations,
    Parallel_Jobs.ExpenseCalculations,
]


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

    try:
        lastProcessTime = lastProcessTimeSearch[0]["processing_timestamp"]

        checkTime = (
            lastProcessTime + reprocessTime * 24 * 60 * 60
        )  # takes the last processing time and adds the reprocess frequency in seconds

        return checkTime < datetime.datetime.now().timestamp()
    except ValueError:
        return True


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

    processingResults = ["Processing Started", True]
    if checkForReprocess(database):
        parallelProcessInterface = threading.Thread(
            target=parallelProcessThread, args=(database, app, None, processingResults), daemon=True
        )
        parallelProcessInterface.start()
        return processingResults
    processingResults = ["No Processing Needed", False]
    return processingResults


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


def parallelProcessThread(database, app, additionalJobs=None, processingResults=None):
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

    jobsCount = len(BACKGROUND_COMMON_JOBS)

    [
        jobs.put(job) for job in BACKGROUND_COMMON_JOBS
    ]  # issues all jobs to the queue. This must be done before the processes are started. They exit if the queue is empty.

    if additionalJobs is not None:
        [jobs.put(job) for job in additionalJobs]

        jobsCount += len(additionalJobs)

    parallelProcessors = [
        multiprocessing.Process(target=processJobsThread, args=(dbCopy, jobs, results), daemon=True)
        for _ in range(maxProcesses)
    ]

    [p.start() for p in parallelProcessors]

    if processingResults is not None:
        processingResults[0] = "Processing..."
        processingResults[1] = True

    jobs.join()  # wait for all jobs to finish

    [jobs.put(None) for _ in range(maxProcesses)]  # tell all processes to exit

    applyResults(database, results, jobsCount)

    if processingResults is not None:
        processingResults[0] = "Processing Complete"
        processingResults[1] = False


def applyResults(
    database: tinydb.TinyDB,
    resultsQueue: multiprocessing.Queue,
    length=None,
):
    """Applies the results of the parallel processing to the database.

    Args:
        database (TinyDB): The database to apply the results to.
        resultsQueue (multiprocessing.Queue): The queue to get the results from.
        jobsQueue (multiprocessing.QueueJoinable): The queue to get the jobs from.
    """

    transients = database.table("Transients")

    if length is None:
        length = resultsQueue.qsize()

    for _ in range(length):
        result = resultsQueue.get()

        transients.upsert(result, tinydb.Query().transient_name == result["transient_name"])


def processJobsThread(databaseCopy, jobsQueue, resultsQueue):
    """Processes the jobs in the jobsQueue.

    Args:
        databaseCopy (TinyDB): The database to process the jobs on.
        jobsQueue (multiprocessing.QueueJoinable): The queue to get the jobs from.
        resultsQueue (multiprocessing.Queue): The queue to put the results in.
    """

    db = deserializeDB(databaseCopy)

    while True:
        job = jobsQueue.get()
        if job is None:
            break

        try:
            result = job(db)
            result["ERROR"] = False
        except Exception as e:
            result = {
                "transient_name": "Error_" + job.__name__,
                "error": str(e),
                "ERROR": True,
            }
        result["processing_timestamp"] = datetime.datetime.now().timestamp()
        resultsQueue.put(result)
        jobsQueue.task_done()
