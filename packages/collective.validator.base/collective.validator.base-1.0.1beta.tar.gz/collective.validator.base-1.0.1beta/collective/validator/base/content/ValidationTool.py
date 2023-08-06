from AccessControl import ClassSecurityInfo

from plone.portlets.interfaces import IPortletContext

from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName

from zope.interface import implements, alsoProvides
from zope.component.globalregistry import getGlobalSiteManager as getSiteManager

from collective.validator.base.config import *
from collective.validator.base.interfaces.interfaces import *
from collective.validator.base.utility import *
import sendattachment

from DateTime import DateTime


schema = Schema((

    StringField(
        name='integrated_validator',
        vocabulary = [('W3c base','IW3c'),('W3c Strict','Iw3cStrict')],
        widget = SelectionWidget(
            label='Integrated-validator type',
            label_msgid='collective.validator.base_label_integrated_validator',
            description='Validator for integrated validation',
            description_msgid='collective.validator.base_help_integrated_validator',
            i18n_domain='collective.validator.base',
        ),
        required=1,
    ),

    BooleanField(
        name='validation_action_enabled',
        default=True,
        widget=BooleanWidget(
            label='Enable integrated validation code',
            label_msgid='collective.validator.base_label_validationactionenabled',
            description='Activating this option you have a strument for the integrated validation code',
            description_msgid='collective.validator.base_help_validationactionenabled',
            i18n_domain='collective.validator.base',
        ),
    ),
        
    StringField(
        name='validator_url',
        vocabulary = [('W3c base','IW3c'),('W3c Strict','Iw3cStrict'),('W3c CSS','ICss')],
        widget = SelectionWidget(
            label='Validator type',
            label_msgid='collective.validator.base_label_validator_url',
            description='Choose the validation type',
            description_msgid='collective.validator.base_help_validator_url',
            i18n_domain='collective.validator.base',
        ),
        required=1,
    ),

    LinesField(
        name='portalTypesList',
        default=('Document','Event','News Item',),
        vocabulary="getPortalTypesVocabulary",
        enforceVocabulary=1,
        widget=MultiSelectionWidget(
            label='Portal types to validate',
            label_msgid='collective.validator.base_label_portal_types_list',
            description='Select all portal type you want to be validated',
            description_msgid='collective.validator.base_desc_portal_types_list',
            i18n_domain='collective.validator.base',
            size=10,
        ),
        required=1,
    ),

    LinesField(
        name='reviewStatesList',
        default=('visible','pending','published',),
        widget=LinesWidget(
            label='Review states to validate',
            label_msgid='collective.validator.base_label_review_states_list',
            description='Insert here a list of review states to validate to limit content type search. Leave empty to ignore filter',
            description_msgid='collective.validator.base_help_review_states_list',
            i18n_domain='collective.validator.base',
        ),
    ),

    IntegerField(
        name='itemsMaxAge',
        required=1,
        default=0,
        widget=IntegerWidget(
            label='Max days from last modification',
            label_msgid='collective.validator.base_label_items_max_age',
            description='Insert the max number of days from last modification of contents. Keep 0 to ignore filter',
            description_msgid='collective.validator.base_help_items_max_age',
            i18n_domain='collective.validator.base',
            size=5,
            maxlength=5,
        ),
    ),

    BooleanField(
        name='sendReport',
        default=True,
        widget=BooleanWidget(
            label='Send report to email address',
            label_msgid='collective.validator.base_label_send_report',
            description='Check to send the validation report to one or more email address',
            description_msgid='collective.validator.base_help_send_report',
            i18n_domain='collective.validator.base',
        ),
    ),

    LinesField(
        name='emailAddresses',
        default_method="getPortalEmailFromAddress",
        widget=LinesWidget(
            label='Delivery addresses',
            label_msgid='collective.validator.base_label_email_addresses',
            description='Report will be send to all email addresses in this list',
            description_msgid='collective.validator.base_help_email_addresses',
            i18n_domain='collective.validator.base',
        ),
    ),

    LinesField(
        name='debugTypesList',
        default=('Document','Event','News Item',),
        vocabulary="getPortalTypesVocabulary",
        enforceVocabulary=1,
        widget=MultiSelectionWidget(
            label='Portal types to validate',
            label_msgid='collective.validator.base_label_debug_types_list',
            description='Run the validation of views for all types selected here',
            description_msgid='collective.validator.base_help_debug_types_list',
            i18n_domain='collective.validator.base',
            size=10,
        ),
    ),

    BooleanField(
        name='sendReportDebug',
        default=True,
        widget=BooleanWidget(
            label='Send report to email address',
            label_msgid='collective.validator.base_label_send_report_debug',
            description='Check to send the validation report of views to one or more email address',
            description_msgid='collective.validator.base_help_send_report_debug',
            i18n_domain='collective.validator.base',
        ),
    ),

    LinesField(
        name='emailAddressesDebug',
        default_method="getPortalEmailFromAddress",
        widget=LinesWidget(
            label='Delivery addresses',
            label_msgid='collective.validator.base_label_email_addresses_debug',
            description='Report will be send to all email addresses in this list',
            description_msgid='collective.validator.base_help_email_addresses_debug',
            i18n_domain='collective.validator.base',
        ),
    ),

),
)


ValidationTool_schema = BaseSchema.copy() + \
    schema.copy()

ValidationTool_schema['title'].widget.visible = {'edit': 'hidden', 'view': 'hidden'}

class ValidationTool(UniqueObject, BaseFolder,DynamicImport):
    implements(IVTPlone)
    security = ClassSecurityInfo()
    __implements__ = (getattr(UniqueObject,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'ValidationTool'

    _at_rename_after_creation = True

    schema = ValidationTool_schema 

    def at_post_edit_script(self):
        self.unindexObject() 

    def runVal(self):
        str = self.dynamic_import()
        for el in str:
            exec(el)
        appo= eval("%s(self)" % self.getValidator_url())
        appo.runValidation()

    def runDebug(self):
        str = self.dynamic_import()
        for el in str:
            exec(el)
        if self.getValidator_url() == 'ICss':
            return 0
        appo= eval("%s(self)" % self.getValidator_url())
        appo.runDebugValidation()

    def validatePage(self,xhtml):
        str = self.dynamic_import()
        for el in str:
            exec(el)
        appo= eval("%s(self)" % self.getIntegrated_validator())
        ret = appo.getValidationResults(xhtml)
        return ret

    def validateReportPage(self,xhtml):
        str = self.dynamic_import()
        for el in str:
            exec(el)
        appo= eval("%s(self)" % self.getValidator_url())
        ret = appo.getValidationResults(xhtml)
        return ret

    def getIntegratedType(self):
        str = self.dynamic_import()
        for el in str:
            exec(el)
        appo= eval("%s(self)" % self.getIntegrated_validator())
        ret = appo.getValidatorType()
        return ret

    def getValUrl(self):
        str = self.dynamic_import()
        for el in str:
            exec(el)
        appo= eval("%s(self)" % self.getValidator_url())
        ret = appo.getValidatorUrl()
        return ret

    security.declarePrivate('getPortalEmailFromAddress')
    def getPortalEmailFromAddress(self):
        """Get a tuple containing portal property 'email_from_address'"""
        portal = self.portal_url.getPortalObject()
        return (portal.getProperty('email_from_address'),)

    security.declarePrivate('getPortalTypesVocabulary')
    def getPortalTypesVocabulary(self):
        portal_types = self.portal_types
        lst = []
        ptypes = portal_types.listTypeTitles() 
        ks = ptypes.keys()
        ks.sort()
        for k in ks:
            lst.append( (k, ptypes[k]) )
        return DisplayList( tuple(lst) )

registerType(ValidationTool, PROJECTNAME)