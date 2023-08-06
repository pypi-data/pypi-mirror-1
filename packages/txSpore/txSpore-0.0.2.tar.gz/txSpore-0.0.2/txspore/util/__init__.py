try:
    from xml.etree.ElementTree import fromstring
except ImportError:
    from ElementTree import fromstring
import re
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


def parseAtomDate(string_datetime):
    pattern = ("(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T"
               "(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
               "(?P<tenths>\.?\d+)(?P<timezone>[A-Za-z]+)")
    match = re.match(pattern, string_datetime)
    data = match.groupdict()
    return datetime(
        int(data.get("year")), int(data.get("month")), int(data.get("day")),
        int(data.get("hour")), int(data.get("minute")),
        int(data.get("second")))


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


def scrubXMLNameSpace(tag):
    match = re.match("{[^}]*}(?P<tag>.*$)", tag)
    return match.groupdict().get("tag")


def validateParameters(inputValue, legalValues):
    if inputValue not in legalValues:
        legalString = "', '".join(legalValues)
        raise ValueError("'%s' is not one of '%s'" % (inputValue, legalString))
    return inputValue
