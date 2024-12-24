import tinydb, json

import multiprocessing


def checkForReprocess(database):
    """Checks the DB for a transient listing the last time the data was processed. Returns true if reprocessing is needed.

    Args:
        database (tinydb): The database to check for a transient.

    Returns:
        bool: True if reprocessing is needed.
    """

    pass


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


def pollForParallelProcessing(database):
    """This functions checks if parallel processing is needed to be run and starts the process if so.

    Args:
        database (tinydb): The database to check for a transient.

    Returns:
        None
    """

    if checkForReprocess(database):
        parallelProcess(database)


def parallelProcess(database):
    """This function starts the parallel processing of the database.

    Args:
        database (tinydb): The database to process.

    Returns:
        None
    """

    settings = database.table("Settings")
    maxProcesses = settings.search(tinydb.Query().setting_name == "Max_Parallel_Processes")[0][
        "setting_value"
    ]
    customJobs
