"""Forms
"""
from string import strip
from datetime import datetime
from zope import event
from Acquisition import aq_inner

from zope.app.component.hooks import getSite
from zope.formlib import form

try:
    from zope.lifecycleevent import ObjectModifiedEvent
except:
    from zope.app.event.objectevent import ObjectModifiedEvent

from icsemantic.core.browser.base import BaseSettingsForm

from Products.Five.formlib import formbase
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from icnews.acquire import interfaces
from icnews.acquire import ICNewsAquireMessageFactory as _


class NewsAcquireSQLServer(BaseSettingsForm):
    """Configlet for the SQL Server"""
    form_name = _(u'News Acquire SQL Server')
    form_fields = form.Fields(interfaces.IicNewsManagementAcquireSQLServer,
                              render_context=True)

    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            # Connect to the SQL server to check parameters.
            import _mysql
            from _mysql_exceptions import ProgrammingError, OperationalError, DatabaseError
            try:
                db = _mysql.connect(host=data["hostname"],
                    user=data["username"],
                    passwd=data["password"],
                    db=data["database"])
                if not data['dbprefix']: data['dbprefix'] = ""
                db.query("SELECT * from %suser" % data['dbprefix'])
                r = db.store_result()
                # Ok.
                event.notify(ObjectModifiedEvent(self.context))
                self.status = _("Updated on ${date_time}",
                    mapping={'date_time': str(datetime.utcnow())}
                    )
            except ( ProgrammingError, OperationalError ), m:
                code, mess = m
                self.status = _('Error ${code}: ${msg}', mapping={'code': code, 'msg': mess})
        else:
            self.status = _('No changes')

