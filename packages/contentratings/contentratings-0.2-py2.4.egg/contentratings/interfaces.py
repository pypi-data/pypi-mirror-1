from zope.interface import Interface
try:
    from zope.annotation.interfaces import IAnnotatable
except ImportError, e:
    # Zope 2.9 support
    from zope.app.annotation.interfaces import IAnnotatable

from zope.schema import Float
from zope.schema import Int
from zope.i18nmessageid import MessageFactory
from zope.app.event.interfaces import IObjectModifiedEvent
_ = MessageFactory('contentratings')

class IEditorRatable(IAnnotatable):
    """Marker interface that promises that an implementing object may be
    rated by an editor using the IEditorialRating interface.
    """

class IUserRatable(IAnnotatable):
    """Marker interface that promises that an implementing object may be
    rated by users using the IUserRating interface.
    """

class IEditorialRating(Interface):
    """Set a single global rating.
    """

    rating = Float(
        title=_(u"Rating"),
        description=_(u"The rating of the current object"),
        required=False
        )

    scale = Int(
        title=_(u"Maximum value"),
        description=_(u"The maximum possible rating"),
        required=False
        )

class IUserRating(Interface):
    """A rating class that allows users to set and adjust their ratings of
       content.
    """

    def userRating(username=None):
        """Return the rating for a given username.

           Returns None if the user has not yet rated the object.
           Returns the average of anonymous ratings if the username is None.
        """

    def rate(rating, username=None):
        """Rate the current object with `rating`.
           Optionally rate the content anonymously if username is None.
        """

    averageRating = Float(
        title=_(u"Average rating"),
        description=_(u"The average rating of the current object"),
        required=True
        )

    numberOfRatings = Int(
        title=_(u"Number of ratings"),
        description=_(u"The number of times the current has been rated"),
        required=True
        )

    scale = Int(
        title=_(u"Maximum value"),
        description=_(u"The maximum possible rating"),
        required=False
        )

class IObjectUserRatedEvent(IObjectModifiedEvent):
    """An event that is emitted when an object is rated by a user"""

class IObjectEditorRatedEvent(IObjectModifiedEvent):
    """An event that is emitted when an object is rated by an editor"""
