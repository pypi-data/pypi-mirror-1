from zope.interface import implements,alsoProvides
from zope.component import adapts

from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName 

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.newsitem import ATNewsItem
basic_atct = (ATDocument,ATEvent,ATNewsItem)

from urllib import quote,urlencode, urlopen
from xml.dom import minidom
from DateTime import DateTime
import string

from collective.validator.base.config import *
from collective.validator.base.interfaces.interfaces import *
from collective.validator.base.content.ATReport import ATReport
from collective.validator.base.content import sendattachment
from collective.validator.base.content.ValidationTool import ValidationTool

import tempfile

class Parser(object):

    security = ClassSecurityInfo()

    def __init__(self, context):
        self.context = context
        self.translation_service = getToolByName(self.context,'translation_service')

    security.declarePrivate('val_type')
    def getValidatorType(self):
        return self.val_type
   
    security.declarePrivate('val_url')
    def getValidatorUrl(self):
        return self.val_url
  
    security.declarePrivate('createResult')
    def createResult(self,resp):
        """create a structure for the result report"""
        results = {'m:errors':{'m:errorcount':0,
                               'm:errorlist':[],
                              },
                   'm:warnings':{'m:warningcount':0,
                                 'm:warninglist':[],
                                },
                   'm:validity':None,
                  }
        try:
            xmldoc = minidom.parseString(resp)
        except:
            return 'wrong file!'
        errors = xmldoc.getElementsByTagName('m:error')
        err_results = []
        for err in errors:
            diz = {}
            diz['m:line'] = int(err.getElementsByTagName('m:line')[0].childNodes[0].nodeValue)
            diz['m:message'] = err.getElementsByTagName('m:message')[0].childNodes[0].nodeValue
            diz['m:col'] = int(err.getElementsByTagName('m:col')[0].childNodes[0].nodeValue)
            err_results.append(diz)
        errs = results['m:errors']
        errs['m:errorcount'] = len(err_results)
        errs['m:errorlist'] = err_results
        results['m:errors'] = errs

        warnings = xmldoc.getElementsByTagName('m:warning')
        warn_results = []
        for warn in warnings:
            diz = {}
            try:
                diz['m:line'] = int(warn.getElementsByTagName('m:line')[0].childNodes[0].nodeValue)
                diz['m:col'] = int(warn.getElementsByTagName('m:col')[0].childNodes[0].nodeValue)
            except IndexError:
                diz['m:line'] = 0
                diz['m:col'] = 0
            diz['m:message'] = warn.getElementsByTagName('m:message')[0].childNodes[0].nodeValue
            warn_results.append(diz)   
        warns = results['m:warnings']
        warns['m:warningcount'] = len(warn_results)
        warns['m:warninglist'] = warn_results
        results['m:warnings'] = warns
        results['m:validity'] = xmldoc.getElementsByTagName('m:validity')[0].childNodes[0].nodeValue == 'true'
        return results

    security.declarePrivate('search')
    def search(self):
        """search the pages to be validated"""
        catalog = getToolByName(self.context,'portal_catalog')
        searchQuery = {}
        searchQuery['portal_type']=list(self.context.getPortalTypesList())
        if self.context.getReviewStatesList():
            searchQuery['review_state']=list(self.context.getReviewStatesList())
        if self.context.getItemsMaxAge():
            searchQuery['modified'] = {'query':DateTime()-self.context.getItemsMaxAge(), 'range':'min'}                 
        return catalog.searchResults(**searchQuery)


    security.declarePrivate('dumpErrors')
    def dumpErrors(self, elist):
        """Render html for validation error structure"""
        stout = "<dl>"
        st = "<dt>%s/%s</dt><br><dd>"
        st += self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='row', \
                                           default="row:", \
                                           context=self.context)
        st +=" %s, "
        st += self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='column', \
                                           default="column:", \
                                           context=self.context)
        st +=" %s</dd><dd><em>%s</em></dd>"
        cnt = 0
        elen = len(elist)
        if not elen: return ""
        try:
            for x in elist:
                cnt+=1
                stout+= st % (cnt, elen, x['m:line'], x['m:col'], x['m:message'])
            return stout+"</dl>"
        except:
            return "wrong list"

    security.declarePrivate('createReportPage')
    def createReportPage(self, validation, title, url):
        """Create the HTML output report for a given HTML source"""
        report = ""
        report+="""<h2>%s</h2><pre><a href="%s">%s</a></pre><p style="margin-top:0px;">""" % (title, url, url)
        parerr = parwarn = 0
        if validation['m:validity']:
            report+= self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='success_valid', \
                                           default="Page validation succesfull<br>", \
                                           context=self.context)
        else:
            report+= self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='unsuccess_valid', \
                                           default="Page validation failed<br>", \
                                           context=self.context)
            if validation.get('m:errors',None):
                parerr = parerr + validation['m:errors']['m:errorcount']
                report += self.createReportErr(validation['m:errors']['m:errorcount'])
                report+=str(self.dumpErrors(validation['m:errors']['m:errorlist']))

            if validation.get('m:warnings',None):
                parwarn = parwarn + validation['m:warnings']['m:warningcount']
                report += self.createReportWarn(validation['m:warnings']['m:warningcount'])
                report+=str(self.dumpErrors(validation['m:warnings']['m:warninglist']))
        report+="</p><br>"
        return (report, parerr, parwarn,validation['m:validity'])

    security.declarePrivate('createReportDocument')
    def createReportDocument(self,fileout,toterr,totwarn,tot_files,valid):
        # Save report in the tool as ATReport
        newId = self.context.generateUniqueId('report')
        self.context.invokeFactory(id=newId, type_name='ATReport',language='')
        now = DateTime().strftime("%d/%m/%Y")
        f = getattr(self.context, newId)
        f.edit(title="Report %s: %s" % (self.val_type,now),
               description = self.createDescription(toterr,totwarn,tot_files),
               text=fileout,
               is_valid=valid,
              )
        return newId

    security.declarePrivate('createDebugReportDocument')
    def createDebugReportDocument(self,fileout,toterr,totwarn,tot_files,valid):
        # Save report in the tool as ATReport
        newId = self.context.generateUniqueId('report')
        self.context.invokeFactory(id=newId, type_name='ATReport',language='')
        now = DateTime().strftime("%d/%m/%Y")
        f = getattr(self.context, newId)
        f.edit(title="Report %s Content Type: %s" %(self.val_type,now),
               #description="%s errors, %s warnings in %s file(s)" % (toterr, totwarn, tot_files),
               description = self.createDescription(toterr,totwarn,tot_files),
               text=fileout,
               is_valid=valid,
              )
        return newId

    security.declarePrivate('createDescription')
    def createDescription(self,toterr,totwarn,tot_files):
        desc = ""
        desc +="%s " %toterr
        desc += self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='tot_errors', \
                                           default="errors", \
                                           context=self.context)

        desc += ", %s " %totwarn
        desc += self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='tot_warnings', \
                                           default="warnings", \
                                           context=self.context)
        desc +=" in %s file(s)" %tot_files
        return desc

    security.declarePrivate('createReportErr')
    def createReportErr(self,errorcount):
        report = ""
        report +=self.translation_service.utranslate( \
                                   domain='collective.validator.base', \
                                   msgid='found', \
                                   default="<h3>Found", \
                                   context=self.context)
        report +=" %s " %errorcount
        report += self.translation_service.utranslate( \
                                   domain='collective.validator.base', \
                                   msgid='tot_errors', \
                                   default="errors", \
                                   context=self.context)
        report += "</h3>"
        return report

    security.declarePrivate('createReportWarn')
    def createReportWarn(self,warncount):
        report = ""
        report +=self.translation_service.utranslate( \
                                   domain='collective.validator.base', \
                                   msgid='found', \
                                   default="<h3>Found", \
                                   context=self.context)
        report +=" %s " %warncount
        report += self.translation_service.utranslate( \
                                   domain='collective.validator.base', \
                                   msgid='tot_warnings', \
                                   default="warnings", \
                                   context=self.context)
        report += "</h3>"
        return report

    security.declarePrivate('createReportMail')
    def createReportMail(self,fileout,toterr, totwarn, tot_files):
        """create the attachment for the mail"""
        str = ""
        str += "<html><head><title>Portal validation</title></head>"
        str += self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='valid_res_for', \
                                           default="<body><h3>Validation Results for", \
                                           context=self.context)
        str +=" %s</h3>" %self.val_type
        str += "<h3>%s " %toterr
        str += self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='tot_errors', \
                                           default="errors", \
                                           context=self.context)
        str +=", %s " %totwarn
        str += self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='tot_warnings', \
                                           default="warnings", \
                                           context=self.context)
        str += " in %s file(s)</h3>" % tot_files
        str += fileout
        str += "<br></body></html>"
        return str

    security.declarePrivate('sendReportAsAttach')
    def sendReportAsAttach(self,str_report,filenamepars, send_from=None, send_to=[], subject="", text="", files=[]):
        """Send the content of a file as attachment to adresses list"""
        tempf = tempfile.NamedTemporaryFile()
        tempf.write(str_report)
        tempf.flush()

        portal = self.context.portal_url.getPortalObject()
        send_from = send_from or self.context.getPortalEmailFromAddress()
        if type(send_from)==tuple and send_from:
            send_from = send_from[0]
        send_to = send_to or list(self.context.getEmailAddresses())
        subject = subject or self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='valid_results_title', \
                                           default="Validation Results", \
                                           context=self.context)
        text1 = self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='generated_report', \
                                           default="Generated validation report for ", \
                                           context=self.context)
        text1 += self.val_type 
        text = text or text1
        files = [tempf.name,]
        server = self.context.MailHost.smtp_host

        sendattachment.send_mail(send_from=send_from,
                                 send_to=send_to,
                                 subject=subject,
                                 text=text,
                                 files=files,
                                 server=server,
                                 mimeb=("text", "html"),
                                 filenamepars=filenamepars,
                                 )
        tempf.close()
