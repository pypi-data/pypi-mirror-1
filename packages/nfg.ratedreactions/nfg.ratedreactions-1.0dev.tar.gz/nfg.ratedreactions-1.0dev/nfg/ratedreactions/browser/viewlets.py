
from zope.component import getMultiAdapter
from nfg.ratedreactions.interfaces import IRatedReactionActivated, IRatedReactionEnabled
from zope.interface import alsoProvides
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
import logging
logger = logging.getLogger('nfg.ratedreaction')

class RatedReactionsViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/reactions.pt')

    def __init__(self, context, request, view, manager):
        super(RatedReactionsViewlet,self).__init__(context, request, view, manager)
        self.__parent__ = view
        self.view = view
        self.manager = manager
        self.portal_state = getMultiAdapter((context, self.request),
            name=u"plone_portal_state")
        alsoProvides(self.context, IRatedReactionActivated) 
        self.reactor = IRatedReactionEnabled(self.context)

    def update(self):
        title = body = rating = None
        if self.request.has_key('nfg.ratedreaction.title'):
            title = self.request['nfg.ratedreaction.title']
        if self.request.has_key('nfg.ratedreaction.body'):
            body = self.request['nfg.ratedreaction.body']
        if self.request.has_key('nfg.ratedreaction.rating'):
            rating = self.request['nfg.ratedreaction.rating']
        if not (title and body and rating) or self.isAnon:
            return None

        author = self.portal_state.member().getId()

        if author is not None:
            self.reactor.addRatedReaction(
                author=author,
                title=title,
                body=body,
                rating=rating)

    def reactions(self):
        return self.reactor.getRatedReactions()

    @property
    def isAnon(self):
        return self.portal_state.anonymous()

    @property
    def isRated(self):
        """ check to see if the current member has rated this object already """
        member = self.portal_state.member().getId()
        return self.reactor.hasRated(author=member)

