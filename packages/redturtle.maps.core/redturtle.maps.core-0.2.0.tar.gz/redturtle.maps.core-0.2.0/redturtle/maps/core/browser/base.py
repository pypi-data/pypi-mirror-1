# -*- coding: utf-8 -*-
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interface import IATContentType, IATDocument, IATEvent, IATNewsItem, IATFile, IATImage, IATLink


class BaseView(BrowserView):

    __call__ = ViewPageTemplateFile('base.pt')
    security = ClassSecurityInfo()

    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    security.declarePublic('getText')
    def getText(self):
        return self.context.getText()
    
InitializeClass(BaseView)
        
                