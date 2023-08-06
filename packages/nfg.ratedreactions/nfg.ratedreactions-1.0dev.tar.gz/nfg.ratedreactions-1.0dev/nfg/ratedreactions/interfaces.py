from zope import schema
from zope.interface import Interface

from nfg.ratedreactions import RatedReactionMessageFactory as _


class IDatabaseSettings(Interface):
    """ Database connection settings
    """
    drivername = schema.ASCIILine(title=_(u"Driver name"),
        description=_(u"The database driver name"),
        default='sqlite',
        required=True)

    hostname = schema.ASCIILine(title=_(u"Host name"),
        description=_(u"The database host name"),
        required=False)

    port = schema.Int(title=_(u"Port number"),
        description=_(u"The database port number."
            "Leave blank to use the default"),
        required=False)

    username = schema.ASCIILine(title=_(u"User name"),
        description=_(u"The database user name"),
        required=False)

    password = schema.ASCIILine(title=_(u"Password"),
        description=_(u"The database password"),
        required=False)

    database = schema.ASCIILine(title=_(u"Database name"),
        description=_(u"The name of the database"),
        default="reactions",
        required=True)


class IRatedReactionAllowed(Interface):
    """Marker interface that promises that an implementing object
    may become IRatedReactionActivated.

    IRatedReactionAllowed is meant to be used in a p4a.subtyper like
    pattern: marking a /class/ IRatedReactionAllowed makes it possible
    for an /instance object/ of that class, to runtime select
    providing IRatedReactionActivated.

    This allows selection of IRatedReactionEnabled adaptation
    on a runtime per-object basis.
    """

class IRatedReactionActivated(Interface):
    """Marker interface that promises that an implementing object.
    may be commented upon using the IRatedReactionEnabled interface.
    """


class IRatedReactionEnabled(Interface):
    """Give and query rated reactions on content objects.
    """

    contextid = schema.Int(
        title= _(u"Context object key"),
        description = _(u"Integer key for the context object being rated."),
        required = True
        )
   
    def addRatedReaction(IRatedReaction):
        """Add a reaction to the context object."""

    def getRatedReactions():
        """Return the IRatedReactions for the context object.
        """

    averageRating = schema.Float(
        title= _(u"Average rating"),
        description = _(u"The average rating of the current object."),
        required = True
        )

    numberOfRatings = schema.Int(
        title = _(u"Number of ratings"),
        description = _(u"The number of rated reactions attached to the current object."),
        required = True
        )


class IRatedReaction(Interface):
    """Represent a rated reaction to a content object.
    """

    contextid = schema.Int(
        title= _(u"Context object key"),
        description = _(u"Integer key for the context object being rated."),
        required = True
        )

    author = schema.TextLine(
        title= _(u"Author"),
        description = _(u"The name (or member id) of the author providing the reaction."),
        required = True
        )

    rating = schema.Int(
        title= _(u"Rating"),
        description = _(u"The rating value of the context object."),
        required = True
        )

    title = schema.TextLine(
        title= _(u"Title"),
        description = _(u"Title headline of the reaction."),
        required = True
        )

    body = schema.Text(
        title= _(u"Body"),
        description = _(u"Body text of the reaction."),
        required = True
        )

    date = schema.Date(
        title= _(u"Date"),
        description = _(u"Creation date of the reaction."),
        required = True
        )

