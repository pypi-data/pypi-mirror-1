"""
The original API seems to be unmaintained. As such, we import what we can use,
and reimplement the rest.
"""
from txspore.original.SporeAPICoreUtils import (
    StatsForCreatureURL as creatureStatsURL,
    ProfileForUserURL as profileInfoURL,
    AssetsForUserURL as assetsForUserURL,
    SporeCastsSubscribedURL as sporeCastsForUserURL,
    AssetsForSporeCastURL as assetsForSporeCastURL,
    AchievementsForUserURL  as achievementsForUserURL,
    InfoForAssetURL as infoForAssetURL,
    CommentsForAssetURL as commentsForAssetURL,
    BuddiesForUserURL as buddiesForUserURL,
    AssetSearch as assetSearchURL
    )
from txspore.url import serverString


def dailyStatsURL():
    return serverString + "/rest/stats"
