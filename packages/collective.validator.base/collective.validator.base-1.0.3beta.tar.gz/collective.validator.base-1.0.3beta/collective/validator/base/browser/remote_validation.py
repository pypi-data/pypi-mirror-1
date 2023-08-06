# -*- coding: utf-8 -*-

from Products.Five import BrowserView


class RemoteValidation(BrowserView):
    """vista per fare l'aggiornamento di TagCloud"""

    def remoteValidation(self):
        """
        @author: andrea cecchi
        Metodo che richiamato aggiorna TagCloud
        """
        self.context.plone_log('INIZIOOOOO')
#        xhtml= self.context.view().encode('utf-8')
        p_ist= self.context.portal_validationtool
        results=p_ist.runVal()
        self.context.plone_log('VALIDAIZONE ESEGUITA')

        
