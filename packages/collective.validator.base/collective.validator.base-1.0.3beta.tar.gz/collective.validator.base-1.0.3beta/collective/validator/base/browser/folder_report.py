from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFDefault.permissions import DeleteObjects

class ReportValidationToolView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.translation_service = getToolByName(self.context,'translation_service')

    def adjustResults(self, brains):
        results = [{'url': x.getURL(),
                    'id': x.id,
                    'data':x.modified.strftime("%d/%m/%Y %H:%M.%S"),
                    'titolo':x.Title,
                    'valid':self.convert(x),
                   } for x in brains]
        res = self.sort_list(results)
        return res

    def convert(self,x):
        if x.getObject().is_valid:
            return "valid.gif"
        return "not_valid.gif"
        
    def getResults(self):
        path = "/".join(self.context.getPhysicalPath())
        pc = getToolByName(self.context,'portal_catalog')
        if self.getSubmitted():
            self.delete_items()
        return self.adjustResults(pc.searchResults(path={"query":path, "depth":1} ))

    def getSubmitted(self):
        if self.request.get('submit') ==  self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='table_delete_button', \
                                           default='Delete', \
                                           context=self.context):
            return True
        return False

    def is_selected_all(self):
        if self.request.get('select') == 'all':  
            return True
        return False

    def delete_items(self):
        plone_utils = getToolByName(self, 'plone_utils')
        args =[]
        args = self.request.get('del')
        try:
            self.context.manage_delObjects(args)
        except:
            if self.context.wl_isLocked():
                self.context.wl_clearLocks()
                self.context.manage_delObjects(args)
        plone_utils.addPortalMessage(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='message_deleted_report', \
                                           default='Selected reports deleted', \
                                           context=self.context))
        self.request.RESPONSE.redirect(self.context.absolute_url()+'/folder_report')

    def sort_list(self,results):
        for i in range(0, len(results) - 1):
            swap_test = False
            for j in range(0, len(results) - i - 1):
                if results[j]['data'] < results[j + 1]['data']:
                    results[j], results[j+1]= results[j+1], results[j]
                    swap_test = True
            if swap_test == False:
                break
        return results