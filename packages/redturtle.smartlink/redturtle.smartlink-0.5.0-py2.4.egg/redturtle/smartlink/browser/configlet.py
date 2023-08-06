from zope.formlib import form
from plone.app.controlpanel.form import ControlPanelForm
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig
from redturtle.smartlink import smartlinkMessageFactory as _
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from plone.app.form.validators import null_validator
from zope.event import notify
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import adapts, getMultiAdapter
from redturtle.smartlink.interfaces import ISmartLink

class SmartlinkConfigForm(ControlPanelForm):
    """Smartlink Control Panel Form"""

    form_fields = form.Fields(ISmartlinkConfig)

    label = _(u"Configuration Panel links")
    description = _(u"Enter a list of front-end links and a list of their appropriate back-end links. Each front-end link matches to the link that occupies the same position in the list of back-end. The number of elements of the lists must be the same.")
    form_name = _("Settings")
    
    def saveFields(self,action,data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
            self._on_save(data)
        else:
            self.status = _("No changes made.")

    @form.action(_(u'label_save_links', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        self.saveFields(action,data)
        
    @form.action(_(u'label_cancel_links', default=u'Cancel'),validator=null_validator,name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/@@smartlink-config')
        return ''

    @form.action(_(u'label_update_links', default=u'Update the existing link'), name=u'update_links')
    def action_update(self, action, data):
        results=self.context.portal_catalog(object_provides=ISmartLink.__identifier__)
        for res in results:
            object=res.getObject()
            object.setRemoteUrl(object.getRemoteUrl())
            object.reindexObject()
        return
