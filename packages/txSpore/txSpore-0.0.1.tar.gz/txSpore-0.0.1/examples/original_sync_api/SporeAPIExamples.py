# -*- coding: utf-8 -*-
import urllib2
import xml.dom.minidom
import os
from datetime import datetime
from string import punctuation
import time

from SporeAPICoreUtils import *

# Examples
# You will need a "Downloads" directory to hold the data downloaded by some of these examples
# See SporeAPICoreUtils.py for the definitions of core functions used in this file
# Email: sshodhan@maxis.com with questions

# Scroll to the bottom and uncomment the various examples to run them

def GetStaticDataForAsset(assetId):
    print "Getting static data for an asset"
    # Fetching Static Data for an asset id
    print "Small PNG:"
    FetchAndSaveSmallPNG(assetId)
    print "Large PNG:"
    FetchAndSaveLargePNG(assetId)
    print "XML:"
    FetchAndSaveXML(assetId)
    print

def GetStaticMaps():
    # The maps that associate block ids to block names and give you some properties about the blocks
    print "Fetching Block and Paint Maps:"
    FetchAndSaveBlockMap("blockmap")
    FetchAndSaveBlockMap("creatureblockmap")
    FetchAndSaveBlockMap("buildingblockmap")
    FetchAndSaveBlockMap("vehicleblockmap")
    FetchAndSaveBlockMap("limbblockmap")
    FetchAndSavePaintMap("paintmap")
    print

def PrintStatsForCreature(creatureId):
    print "Getting Stats for Creature " + creatureId
    stats = GetStatsForCreature(creatureId)
    stats.Print()
    print

def PrintCommentsForAsset(assetId):
    print "Getting Comments for " + assetId
    comments = GetCommentsForAsset(assetId)
   
    for i in range(0, len(comments)):
        print comments[i].mSender + ": " + comments[i].mMessage 
   
    print

def PrintTagsForAsset(assetId):
    print "Getting Tags for " + assetId
    tags = GetTagsForAsset(assetId)
    for i in range(0, len(tags)):
        print tags[i]
    print
    
def PrintDescriptionForAsset(assetId):
    print "Getting Description for " + assetId
    desc = GetDescriptionForAsset(assetId)
    for i in range(0, len(desc)):
        print desc[i]
    print


def PrintAssetIdsForUser(username):
    ids  = GetAssetIdsForUser(username)
    for i in range(0, len(ids)):
        print ids[i]

def SaveCreaturesForUser(username):
    ids = GetAssetIdsOfTypeForUser(username, "CREATURE")
    for i in range(0, len(ids)):
        FetchAndSaveSmallPNG(ids[i])


def PrintAchievementsForUser(username):
    a= GetAchievementsForUser(username, 0, 1000)
    for i in range(0, len(a)):
        print a[i].mName
        print a[i].mText
        print
    print

def SaveProfilePicForUser(username):
    GetProfileForUser(username) # You can extend this to get tagline etc.

def PrintBuddiesForUser(username):
    buddyList = GetBuddiesForUser(username)
    for i in range(0, len(buddyList)):
        print buddyList[i]

def DemoSearches():
    print "Downloading assets from searches:"
    print "5 featured creatures:"
    FetchAssetsInSearch("FEATURED", 0, 5, "CREATURE")
    print
    print "5 most popular ufos:"
    FetchAssetsInSearch("TOP_RATED", 0, 5, "UFO")
    print
    print "5 random vehicles:"
    FetchAssetsInSearch("RANDOM", 0, 5, "VEHICLE")
    print

def SaveAssetsFromSubscribedSporecasts(username):
    sporecasts = GetSporeCastsForUser(username)
    n = 2
    for i in range(0, len(sporecasts)):
        # Just get two assets from each sporecast
        print "Getting " + str(n) + " assets from sporecast " + sporecasts[i]
        GetAssetsForSporeCast(sporecasts[i], 0, n)
        print
   


# Uncomment the tests below to run them!
# Outputs are in respective files in ./Downloads/
# or printed to screen

#PrintStatsForCreature("500267423060")
#GetStaticDataForAsset("500267423060")
#DemoSearches()
#PrintCommentsForAsset("500279163105")
#PrintTagsForAsset("500279163105")
#PrintDescriptionForAsset("500279163105")
#PrintAssetIdsForUser("MaxisEditorDan")
#SaveCreaturesForUser("MaxisCactus") 
#PrintAchievementsForUser("MaxisCactus")
#SaveProfilePicForUser("MaxisCactus")
#PrintBuddiesForUser("MaxisDangerousYams")
#SaveAssetsFromSubscribedSporecasts("MaxisDangerousYams") 
    
