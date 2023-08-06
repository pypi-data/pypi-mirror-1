from zope.interface import Interface, implements
from zope.component import adapts, getMultiAdapter
from zope.event import notify
from zope.formlib import form

from plone.app.controlpanel.events import ConfigurationChangedEvent
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.form.validators import null_validator
from plone.fieldsets import FormFieldsets
from plone.protect import CheckAuthenticator

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty, SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from collective.validator.base.interfaces.interfaces import *

class IValidationToolControlPanelAdapter(SchemaAdapterBase):
    
    implements(IWebValidator)
    adapts(IPloneSiteRoot)
   
    def __init__(self, context):
        super(IValidationToolControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_validationtool')
        
#area config
    
    def get_integrated_validator(self):
        return self.context.getIntegrated_validator()

    def set_integrated_validator(self, value):
        self.context.setIntegrated_validator(value)
    
    def get_validation_action_enabled(self):
         return self.context.getValidation_action_enabled()
    
    def set_validation_action_enabled(self, value):
        pa = getToolByName(self.context, 'portal_actions')
        for action in pa.listActions():
            if action.getId() == 'validationtool':
                if (value):
                    action.visible=1
                else:
                    action.visible=0
        return self.context.setValidation_action_enabled(value)

    integrated_validator = property(get_integrated_validator, set_integrated_validator)
    validation_action_enabled =  property(get_validation_action_enabled, set_validation_action_enabled)
    
#area validation

    def get_validator_url(self):
        return self.context.getValidator_url()

    def set_validator_url(self, value):
        self.context.setValidator_url(value)
    
    def get_portalTypesList(self):
        return self.context.getPortalTypesList()

    def set_portalTypesList(self, value):
        self.context.setPortalTypesList(value)
    
    def get_reviewStatesList(self):
        return self.context.getReviewStatesList()

    def set_reviewStatesList(self, value):
        self.context.setReviewStatesList(value)
    
    def get_itemsMaxAge(self):
        return self.context.getItemsMaxAge()

    def set_itemsMaxAge(self, value):
        self.context.setItemsMaxAge(value)
    
    def get_emailAddresses(self):
        return self.context.getEmailAddresses()

    def set_emailAddresses(self, value):
        self.context.setEmailAddresses(value)
    
    validator_url = property(get_validator_url, set_validator_url)
    portalTypesList = property(get_portalTypesList, set_portalTypesList)
    reviewStatesList = property(get_reviewStatesList, set_reviewStatesList)
    itemsMaxAge = property(get_itemsMaxAge, set_itemsMaxAge)
    emailAddresses = property(get_emailAddresses, set_emailAddresses)
    
    sendReport = ProxyFieldProperty(IValidationToolValidationSchema['sendReport'])
    
#area debug
    def get_debugTypesList(self):
        return self.context.getDebugTypesList()

    def set_debugTypesList(self, value):
        self.context.setDebugTypesList(value)
    
    def get_emailAddressesDebug(self):
        return self.context.getEmailAddressesDebug()

    def set_emailAddressesDebug(self, value):
        self.context.setEmailAddressesDebug(value)
        
    debugTypesList = property(get_debugTypesList, set_debugTypesList)
    emailAddressesDebug = property(get_emailAddressesDebug, set_emailAddressesDebug)
    
    sendReportDebug = ProxyFieldProperty(IValidationToolDebugSchema['sendReportDebug'])

config = FormFieldsets(IValidationToolConfigSchema)
config.id = 'config'
config.label = _(u'Config')

validation = FormFieldsets(IValidationToolValidationSchema)
validation.id = 'validation'
validation.label = _(u'Validation')

debug = FormFieldsets(IValidationToolDebugSchema)
debug.id = 'debug'
debug.label = _(u'Debug')

class ValidationToolControlPanel(ControlPanelForm):

    form_fields = FormFieldsets(config, validation, debug)

    label = _('ValidationTool Settings')
    description = _('')
    form_name = _('ValidationTool Settings')
    
    def saveFields(self,action,data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
            notify(ConfigurationChangedEvent(self, data))
            self._on_save(data)
        else:
            self.status = _("No changes made.")
        portal_val = getToolByName(self.context, 'portal_validationtool')
        str = portal_val.getIntegratedType()
        pa = getToolByName(self.context, 'portal_actions')
        str1 = _('Validate')
        pa.document_actions.validationtool.title = str1 + ' ' + str
        return portal_val

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        self.saveFields(action,data)
	

    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/@@validationtool-controlpanel')
        return ''
    
    @form.action(_(u'save_and_valid',default=u'Save and Run Validate'), name=u'save_validate')
    def run_validation(self, action, data):
        portal_val = self.saveFields(action,data)
        portal_val.runVal()
        return 

    @form.action(_(u'save_and_debug',default=u'Save and Run Debug'), name=u'save_debug')
    def run_debug(self, action, data):
        portal_val = self.saveFields(action,data)
        if  portal_val.runDebug() == 0:
            self.status = _("Debug is not a Css function")
        return

    @form.action(_(u'go_report',default=u'Go to Report Page'), name=u'go_report')
    def go_report(self, action, data):
        CheckAuthenticator(self.request)
        self.request.response.redirect(self.context.portal_url()+"/portal_validationtool/folder_report")
        return

    def _on_save(self, data=None):
        pass