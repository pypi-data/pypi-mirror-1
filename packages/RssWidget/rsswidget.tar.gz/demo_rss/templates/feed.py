import feedparser


def getFeeds(feeds):
    parsedfeeds = []
    parsed=None
    feed=None
    
    for feed in feeds.keys():
        parsed=feedparser.parse(feeds[feed])
        parsedfeeds.append(parsed) 
    return parsedfeeds

