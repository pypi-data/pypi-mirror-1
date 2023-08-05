from zope.schema import Float, Int
from zope.interface import Interface
from zope.annotation.interfaces import IAnnotatable
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('wc.rating')

class IRatable(IAnnotatable):
    """Marker interface that promises that an implementing object maybe
    rated using ``IRating`` annotations.
    """

class IRating(Interface):
    """Give and query rating about objects, such as recipes.
    """

    def rate(rating):
        """Rate the current object with `rating`.
        """

    average = Float(
        title=_(u"Average rating"),
        description=_(u"The average rating of the current object"),
        required=True
        )

    numberOfRatings = Int(
        title=_(u"Number of ratings"),
        description=_(u"The number of times the current has been rated"),
        required=True
        )
