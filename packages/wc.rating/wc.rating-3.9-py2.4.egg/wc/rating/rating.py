import zope.component
import zope.interface
import persistent.list
from zope.annotation import factory
from wc.rating.interfaces import IRating, IRatable

class Rating(persistent.Persistent):
    zope.interface.implements(IRating)
    zope.component.adapts(IRatable)

    def __init__(self):
        self.average = 0.0
        self.numberOfRatings = 0
        self.ratings = persistent.list.PersistentList()

    def rate(self, rating):
        ratings = self.ratings
        ratings.append(float(rating))
        self.numberOfRatings += 1
        self.average = sum(ratings)/len(ratings)

rating_adapter = factory(Rating)
