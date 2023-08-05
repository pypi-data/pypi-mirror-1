"""Models for prediction of user ratings of items using collaborative filtering.

The classes `DistanceModel`, `SimpleSimilarityModel`, and `SMSimilarityModel`
use different methods for judging the similarity of two users given their
rating histories.

The `getRecommendations` method for the above classes returns a list of
items and their scores (how relevant they are to the given user), sorted
from most recommended to least recommended. It does this by weighting other
users' preferences by their similarity to the user for whom recommendations
are being requested.

The example below uses the AudioScrobbler service to obtain preference data,
then uses `getRecommendations` to suggest artists for a given user.

Usage
-----
>>> from consensus import DistanceModel, SimpleSimilarityModel, SMSimilarityModel
>>> def loadPreferences():
...    d = shelve.open("scrobbler.pickle")
...    judgeRatings = {}
...    for user, artistsInfo in d.iteritems():
...        judgeRatings[user] = {}
...        for artistName, playCount in artistsInfo:
...            judgeRatings[user][artistName] = playCount
...    return judgeRatings

>>> judgeRatings = loadPreferences()
>>> distance = DistanceModel(judgeRatings)
>>> similarity = SimpleSimilarityModel(judgeRatings)
>>> sm_similarity = SMSimilarityModel(judgeRatings)

>>> [artist for artist, score in distance.getRecommendations('eggs_again', limit=10)]
[u'Sufjan Stevens', u'Elliott Smith', u'Broken Social Scene', u'Belle and Sebastian',
 u'The Beatles', u'Wilco', u'The Decemberists', u'Interpol', u'Bright Eyes', u'Beck']

>>> [artist for artist, score in similarity.getRecommendations('eggs_again', limit=10)]
[u'Sufjan Stevens', u'Elliott Smith', u'Broken Social Scene', u'The Beatles',
 u'Belle and Sebastian', u'Wilco', u'Interpol', u'The Decemberists', u'Beck',
 u'Bright Eyes']

>>> [artist for artist, score in sm_similarity.getRecommendations('eggs_again', limit=10)]
[u'Sufjan Stevens', u'Elliott Smith', u'Broken Social Scene', u'Belle and Sebastian',
 u'The Beatles', u'Interpol', u'Wilco', u'The Decemberists', u'Bright Eyes',
 u'Death Cab for Cutie']
"""
import math
from operator import itemgetter

class Model(object):
    """The base class for all collaborative filtering models.
    For subclassing only.
    """
    def __init__(self, judgeRatings=None, judges=None):
        """Initialize the model with a group of judges and their rating histories

        `judgeRatings` is a dictionary mapping judges to their rating histories.
        Rating histories are represented as dictionaries mapping items to their
        rating by that judge. If a list `judges` is given as a list of judges,
        `judgeRatings` will be initialized with empty rating histories.
        """
        if judgeRatings:
            self.judgeRatings = judgeRatings
        elif judges:
            self.judgeRatings = dict((j, {}) for j in judges)
        else:
            self.judgeRatings = {}

    def similarity(self, j1, j2, neutralScore=0, items=None):
        """Calculate the similarity of judges j1 and j2.

        If `neutralScore` is given, it is the midpoint of the rating scale
        being used.

        If a list of `items` is given, the judges' ratings for only those
        items will be considered when determining similarity.
        """
        raise NotImplementedError("Subclasses must implement a similarity function")

    def getNeighbors(self, judge, limit=None, threshold=None, neutralScore=0,
                     items=None):
        """Get a sorted list of neighbors for the given judge, where neighbors
        are defined as judges with preferences most similar to the given judge.

        `judge` is the user for whom a list of neighbors will be calculated.

        If `limit` is given, it will limit the length of the list of neighbors
        being returned. If `threshold` is given, it specifies the cutoff point
        for which neighbors will be included. This will be highly dependent on
        which model is chosen. A lower `threshold` will result in fewer
        neighbors being returned.

        `neutralScore` and `items` are as defined in `Model.similarity`.
        """
        neighbors = []
        for j in self.judgeRatings:
            if j == judge:
                continue
            similarity = self.similarity(j, judge, neutralScore, items)
            if threshold and similarity > threshold:
                continue
            neighbors.append((j, similarity))
        return sorted(neighbors, key=itemgetter(1))[:limit]

    def getRecommendations(self, judge, limit=None, neutralScore=0,
                           items=None):
        """Return a list of items and their scores (how relevant they are to
        the given judge), sorted from most recommended to least recommended.

        `limit`, `neutralScore`, and `items` are all as defined in
        `Model.getNeighbors`.
        """
        recommendScores = {}
        for j, ratings in self.judgeRatings.iteritems():
            for i, rating in ratings.iteritems():
                if rating > neutralScore and i not in self.judgeRatings[judge]:
                    recommendScores.setdefault(i, 0)
                    sim = self.similarity(j, judge, neutralScore, items)
                    if not sim:
                        continue
                    recommendScores[i] += rating * sim

        return sorted(((i, s) for (i, s) in recommendScores.iteritems()),
                      key=itemgetter(1), reverse=True)[:limit]

class DistanceModel(Model):
    """Uses the vector distance in n-dimensional space defined by the users' ratings for n items"""
    def similarity(self, j1, j2, neutralScore=0, items=None):
        """See `Model.similarity` for argument information."""
        if items is None:
            items = set(self.judgeRatings[j1]) & set(self.judgeRatings[j2])
        distance = math.sqrt(sum(pow(self.judgeRatings[j1].get(i, neutralScore) - \
                                 self.judgeRatings[j2].get(i, neutralScore),
                                 2) for i in items))
        if not distance:
            return 0 #This could be incorrect, if the two users have exactly the same ratings for the items they've both rated
        similarity = 1.0 / (distance)
        return similarity

class SimpleSimilarityModel(Model):
    """Uses a simple function where a larger intersection of preferred items results in greater similarity"""
    def similarity(self, j1, j2, neutralScore=0, items=None):
        """See `Model.similarity` for argument information."""
        if items is None:
            items = set(self.judgeRatings[j1]) & set(self.judgeRatings[j2])
        similarityCount = len([item for item in items if \
                               self.judgeRatings[j1][item] > neutralScore and \
                               self.judgeRatings[j2][item] > neutralScore])
        return similarityCount

class SMSimilarityModel(Model):
    """Uses the constrained Pearson correlation function (Shardanand & Maes 1995)"""
    def similarity(self, j1, j2, neutralScore=0, items=None):
        """See `Model.similarity` for argument information."""
        if items is None:
            items = set(self.judgeRatings[j1]) & set(self.judgeRatings[j2])
        top = bottomleft = bottomright = 0
        for item in items:
            top += (self.judgeRatings[j1][item] - neutralScore) * \
                   (self.judgeRatings[j2][item] - neutralScore)
            bottomleft += math.pow(self.judgeRatings[j1][item], 2)
            bottomright += math.pow(self.judgeRatings[j2][item], 2)
        if not bottomleft or not bottomright:
            return 1.0
        similarity = float(top) / math.sqrt(bottomleft * bottomright)
        return similarity

__all__ = ['Model', 'DistanceModel', 'SimpleSimilarityModel', 'SMSimilarityModel']

__author__ = "Brian Beck <exogen@gmail.com>, Mike Rotondo <mrotondo@gmail.com>"
__copyright__ = "Copyright 2006, Brian Beck & Mike Rotondo"