import os
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone.memoize.compress import xhtml_compress
from ilrt.contentmigrator.ContentMigrator.ContentExporter import ContentExporter
from ilrt.contentmigrator.ContentMigrator.interfaces import IContentExporterTool

from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot


class ContentExporterView(BrowserView, ContentExporter):
    ''' This allows for zcml config of the management screens for the tool '''

    implements(IContentExporterTool)
    _template = ViewPageTemplateFile('templates/exportContentMigrator.pt')
    savepath = os.path.join(INSTANCE_HOME, 'var', 'structure')
    out = []

    def __call__(self):
        """ use the root form value to flag run export """
        request = getattr(self,'REQUEST',{})
        root = request.get('root','')
        users = request.get('exportusers',None)
        if root:
            self.out = []
            self.export(root=root,
                        portal=getUtility(ISiteRoot),
                        users=users,
                        request=request)
        return xhtml_compress(self._template())

    def getLog(self):
        """ return the out log file of export actions """
        return self.out 
