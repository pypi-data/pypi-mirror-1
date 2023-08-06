
from zope.component import getUtility
from zope.formlib import form

from plone.app.controlpanel.form import ControlPanelForm

from collective.lead.interfaces import IDatabase

from nfg.ratedreactions.interfaces import IDatabaseSettings
from nfg.ratedreactions import RatedReactionMessageFactory as _

def database_settings(context):
    return getUtility(IDatabaseSettings)

class RatedReactionDatabaseControlPanel(ControlPanelForm):
    form_fields = form.FormFields(IDatabaseSettings)
    form_name = _(u"Rated Reaction Database settings")
    label = _(u"Rated Reaction Database settings")
    description = _(u"Please enter the appropriate connection settings"
        "for the database")

    def _on_save(self, data):
        ControlPanelForm._on_save(self, data)
        db = getUtility(IDatabase, name="nfg.ratedreactions")
        db.invalidate()

