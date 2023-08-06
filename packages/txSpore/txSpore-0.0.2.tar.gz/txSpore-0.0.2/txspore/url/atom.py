from txspore.url import serverString


def assetsForUserURL(username):
    return "%s/atom/assets/user/%s" % (serverString, username)


def eventsForUserURL(username):
    return "%s/atom/events/user/%s" % (serverString, username)


def eventsForAssetURL(assetID):
    return "%s/atom/events/asset/%s" % (serverString, assetID)


def sporeCastFeedURL(sporeCastID):
    return "%s/atom/sporecast/%s" % (serverString, sporeCastID)


def assetSearchURL(searchType, start, length):
    return "%s/atom/assets/view/%s/%s/%s" % (
        serverString, searchType, start, length)

