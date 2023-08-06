from Products.Five.browser.resource import FileResource

from zope.app.component.hooks import getSite
from z3c.zrtresource import processor, replace


class ZRTFileResource(FileResource):

    def GET(self):
        """ Processes the original resource and returns a modified one. """
        data = super(ZRTFileResource, self).GET()
        # Process the file
        p = processor.ZRTProcessor(data, commands={'replace': replace.Replace})
        return p.process(getSite(), self.request)
