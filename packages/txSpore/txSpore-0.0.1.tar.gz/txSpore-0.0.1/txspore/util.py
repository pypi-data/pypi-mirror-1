try:
    from xml.etree.ElementTree import fromstring
except ImportError:
    from ElementTree import fromstring
from datetime import datetime

from twisted.python import log

from txspore.original.SporeAPICoreUtils import (
    UnicodeString as toUnicode,
    )


def logError(error, exceptionOverride=None, message=""):
    if not message:
        message = error.getErrorMessage()
    message = "ERROR: %s" % message
    log.msg(message)
    if not exceptionOverride:
        error.raiseException()
    else:
        if not message:
            message = error.getErrorMessage()
        raise exceptionOverride(message)


def XML(xmlBytes):
    return fromstring(xmlBytes.strip())


def parseXMLDate(string_datetime):
    string_date, string_time = string_datetime.split()
    year, month, day = [int(x) for x in string_date.split("-")]
    hour, minute, second = [int(float(x)) for x in string_time.split(":")]
    return datetime(year, month, day, hour, minute, second)


def stringToList(string):
    string = string.strip()
    if "," in string:
        splitter = ","
    elif ";" in string:
        splitter = ";"
    else:
        splitter = " "
    if string.startswith("["):
        startIndex = 1
    else:
        startIndex = 0
    if string.endswith("]"):
        splits = string[startIndex:-1].split(splitter)
    else:
        splits = string[startIndex:].split(splitter)
    return [x.strip() for x in splits if x]
