from cElementTree import ElementTree, fromstring
from urllib import urlopen
import shelve
import time
import sys

def getTopArtists(user):
    url = "http://ws.audioscrobbler.com/1.0/user/%s/topartists.xml"
    try:
        node = ElementTree(file=urlopen(url % user))
    except (AttributeError, SyntaxError):
        return []
    time.sleep(1.5)
    return [(a.find('name').text, int(a.find('playcount').text)) for a in node.findall('artist')]

def getNeighbours(user):
    url = "http://ws.audioscrobbler.com/1.0/user/%s/neighbours.xml"
    try:
        node = ElementTree(file=urlopen(url % user))
    except (AttributeError, SyntaxError):
        return []
    time.sleep(1.5)
    return [u.get('username') for u in node.findall('user')]

def getFriends(user):
    url = "http://ws.audioscrobbler.com/1.0/user/%s/friends.xml"
    try:
        node = ElementTree(file=urlopen(url % user))
    except (AttributeError, SyntaxError):
        return []
    time.sleep(1.5)
    return [u.get('username') for u in node.findall('user')]

def getUsers(start_user='eggs_again', limit=1000):
    limit = int(limit)
    d = shelve.open("scrobbler.pickle")
    queue = [start_user]
    try:
        while len(d) < limit and queue:
            user = queue.pop(0)
            if len(queue) < limit - len(d):
                queue.extend([u for u in set(getNeighbours(user)) if u not in queue and u not in d])
                if len(queue) > limit - len(d):
                    queue = queue[:limit - len(d)]
            d[user] = [(unicode(a), count) for (a, count) in getTopArtists(user)]
            print "Wrote %s's top artists: %r" % (user, ', '.join( a[0] + ':' + str(a[1]) for a in d[user]))
            print "I have %d users saved and %d users in the queue." % (len(d), len(queue))
    finally:
        d.sync()
        d.close()

if __name__ == "__main__":
    getUsers(*sys.argv[1:])

from consensus import DistanceModel, SimpleSimilarityModel, SMSimilarityModel

def loadPreferences():
    d = shelve.open("scrobbler.pickle")
    judgeRatings = {}
    for user, artistsInfo in d.iteritems():
        judgeRatings[user] = {}
        for a, count in artistsInfo:
            judgeRatings[user][a] = count
    return judgeRatings

judgeRatings = loadPreferences()
distance = DistanceModel(judgeRatings)
similarity = SimpleSimilarityModel(judgeRatings)
sm_similarity = SMSimilarityModel(judgeRatings)
