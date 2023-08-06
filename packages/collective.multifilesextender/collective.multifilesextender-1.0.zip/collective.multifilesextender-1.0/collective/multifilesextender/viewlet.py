from zope.component import getMultiAdapter

from plone.app.layout.viewlets.common import ViewletBase 

from AccessControl import getSecurityManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class MultiFilesViewlet(ViewletBase):
    index = ViewPageTemplateFile('viewlet.pt')

    def update(self):
        super(MultiFilesViewlet, self).update()

    def available(self):
        return self.context.Schema().getField('multifile').getAccessor(self.context)()

    def multifilefield(self):
        return self.context.Schema().getField('multifile')
        