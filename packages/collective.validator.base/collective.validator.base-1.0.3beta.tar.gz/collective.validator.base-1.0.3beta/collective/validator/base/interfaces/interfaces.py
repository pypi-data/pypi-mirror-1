from zope.interface import Interface
from zope.schema import *
from zope.schema import vocabulary as schemavocab

from Products.CMFCore.utils import getToolByName 
from Products.CMFPlone import PloneMessageFactory as _

class IValidationToolConfigSchema(Interface):
    """ ValidationTool Schema """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.translation_service = getToolByName(self.context,'translation_service')

    integrated_validator =Choice(title=u'Validation Type',
                   description=_(u'Choose the validation type'),
                   vocabulary= 'Available integrated_val',
                   required=True,
                   )
                  
    validation_action_enabled = Bool(title=_(u'Enable integrated validation code'),
                                description=_(u'Activating this option you have a strument for the integrated validation code'),
                                default=True)

class IValidationToolValidationSchema(Interface):

    """ ValidationTool Schema """

    validator_url =Choice(title=u'Validation Type',
                   description=_(u'Choose the validation type'),
                   vocabulary= 'Available Validators',
                   required=True,
                   )

    portalTypesList = Set(title=_(u'Portal_types to validate'),
                            description=_(u'Select all portal_types you want to be validated'),
                            value_type = Choice(vocabulary= 'Available Portal_types'),
                            required=True)
                          
    reviewStatesList = List(title=_(u'Review states to validate'),
                                description=_(u'Insert here a list of review states to validate to limit content type search. Leave empty to ignore filter'),
                                value_type = TextLine(),
                                required=False)
                            
    itemsMaxAge = Int(title=_(u'Max days from last modification'),
                                description=_(u'Insert the max number of days from last modification of contents. Keep 0 to ignore filter'),
                                default=0,
                                required=True)
    
    sendReport = Bool(title=_(u'Send report to email address'),
                                description=_(u'Check to send the validation report to one or more email address'),
                                default=True)
                                
    emailAddresses = List(title=_(u'Delivery addresses'),
                                description=_(u'Report will be send to all email addresses in this list'),
                                value_type = TextLine(),
                                required=False)
 
   
class IValidationToolDebugSchema(Interface):
    """ ValidationTool Schema """
  
    debugTypesList = Set(title=_(u'Portal_types to validate'),
                            description=_(u'Select all portal_types you want to be validated'),
                            value_type = Choice(vocabulary= 'Available Portal_types'),
                            required=True)
    
    sendReportDebug = Bool(title=_(u'Send report to email address'),
                                description=_(u'Check to send the validation report to one or more email address'),
                                default=True)
    
    emailAddressesDebug = List(title=_(u'Delivery addresses'),
                        description=_(u'Report will be send to all email addresses in this list'),
                        value_type = TextLine(),
                        required=False)


class IWebValidator(IValidationToolConfigSchema, IValidationToolValidationSchema, IValidationToolDebugSchema):
    """ Marker interface for the ValidationTool """
    
    def getValidatorUrl():
        """return the validator url"""

    def getValidationResults(xhtml):
        """send the pages to validator"""

    def createResult(xmldoc):
         """create the structure to show results"""
    
    def search():
        """search the pages to be validated"""

    def dumpErrors(elist):
        """Commento temporaneo"""

    def createReportPage(validation, title, url):
        """create a report page"""

    def createReportDocument(fileout,toterr,totwarn,tot_files,valid):
        """Save report in the tool as ATReport"""

    def createDebugReportDocument(fileout,toterr,totwarn,tot_files,valid):
        """Save report in the tool as ATReport"""

    def createDescription(toterr,totwarn,tot_files):
        """create a string for description in the document"""

    def createReportErr(errorcount):
        """create a string for error-list in the document"""

    def createReportWarn(warncount):
        """create a string for warning-list in the document"""

    def runValidation():
        """select the pages to be validated and call getValidationResults"""

    def runDebugValidation():
        """Run a validation on other kind of pages,like edit"""

    def createReportMail(fileout,toterr, totwarn, tot_files):
        """create the attachment for the mail"""

    def sendReportAsAttach(f, filenamepars, send_from=None, send_to=[], subject="", text="", files=[]):
        """send report by email"""

    def setBaseType(tmpobject):
        """set the base type"""

    def at_post_edit_script():
        """some comment"""

class IDynamicImport(Interface):
    """Marker interface for the dinamic import"""

class IATReport(Interface):
    """Marker interface for ATReport document"""

class IVTPlone(Interface,IDynamicImport):
    """Marker interface for the validation tool."""

class IPortalTransformsTool(Interface):
    """Marker interface for the portal_transforms tool."""


class IBaseValidationType(Interface):
    """Interface rappresenting basic content type to validate"""
    
class IValidable(Interface):
    """Interface rappresenting a validable type
    """
    
    def isValid():
        """Return the tuple (success, validation_report)
        """
