import os

# Common functions to be used throughout the project


def CleanedFileName(FileName):
    """Takes Path String and returns a cleaned version of the string that can be used as a file name

    Args:
        FileName (str): file name to be cleaned NOT WHOLE PATH NOR EXTENSION

    Returns:
        str: Cleaned file name
    """
    FileName = FileName.replace(" ", "_")
    FileName = FileName.replace("/", "-")
    FileName = FileName.replace("\\", "-")
    FileName = FileName.replace(":", "-")
    FileName = FileName.replace("*", "-")
    FileName = FileName.replace("?", "-")
    FileName = FileName.replace('"', "-")
    FileName = FileName.replace("<", "-")
    FileName = FileName.replace(">", "-")
    FileName = FileName.replace("|", "-")
    FileName = FileName.replace(".", "-")  # Remove false file extension

    return FileName
