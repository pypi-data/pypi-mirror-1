from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
from worldcookery.interfaces import IRating, IRatable

KEY = "worldcookery.rating"

class Rating(object):
    implements(IRating)
    adapts(IRatable)

    def __init__(self, context):
        self.context = self.__parent__ = context
        annotations = IAnnotations(context)
        mapping = annotations.get(KEY)
        if mapping is None:
            blank = {'average': 0.0, 'ratings': PersistentList()}
            mapping = annotations[KEY] = PersistentDict(blank)
        self.mapping = mapping

    def rate(self, rating):
        ratings = self.mapping['ratings']
        ratings.append(float(rating))
        self.mapping['average'] = sum(ratings)/len(ratings)
        info = Attributes(IRating, 'averageRating', 'numberOfRatings')
        notify(ObjectModifiedEvent(self.context, info))

    @property
    def averageRating(self):
        return self.mapping['average']

    @property
    def numberOfRatings(self):
        return len(self.mapping['ratings'])