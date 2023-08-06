from zope.interface import implements
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
import DateTime
import sqlalchemy as sql
from collective.lead.interfaces import IDatabase

from plone.memoize.instance import memoize
from nfg.ratedreactions.interfaces import IRatedReactionEnabled
from nfg.ratedreactions.db import RatedReaction
import logging
import sha
logger = logging.getLogger('nfg.ratedreaction')

class RatedReactionEnabler(object):
    """Store and retrieve rated reactions.
    """

    implements(IRatedReactionEnabled)

    def __init__(self, context):
        self.contextid = getUtility(IIntIds).register(context)
        self.db = getUtility(IDatabase, name="nfg.ratedreactions")
        self.reactions = []

    def addRatedReaction(self, 
                         author=None, 
                         rating=None, 
                         title=None, 
                         body=None):

        new = RatedReaction()
        new.contextid = self.contextid
        new.author = author
        new.rating = rating
        new.title = title
        new.body = body
        new.date = DateTime.DateTime().ISO()
        self.db.session.save(new)
        self.db.session.flush()

    @memoize
    def getRatedReactions(self):
        q = self.db.session.query(RatedReaction)
        q = q.filter(RatedReaction.contextid == self.contextid)
        return q.all()

    @property
    def averageRating(self):
        avg = self.db.connection.scalar("SELECT AVG(rating) FROM ratedreaction WHERE contextid=%s", self.contextid)
        if avg:
            return int(round(float(avg)))
        else:
            return 0

    @property
    def numberOfRatings(self):
        return self.db.connection.scalar("SELECT COUNT(1) FROM ratedreaction WHERE contextid=%s", self.contextid)

    @memoize
    def hasRated(self, author=None):
        q = self.db.session.query(RatedReaction)
        q = q.filter(RatedReaction.author == author)
        q = q.filter(RatedReaction.contextid == self.contextid)
        r = len(q.all())
        if r: 
            return True
        else:
            return False

