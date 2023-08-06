from Products.Five import BrowserView
from collective.gallery import flickr
from collective.gallery import picasa
from zope import interface
from collective.gallery.interfaces import IAlbum


class Link(BrowserView):
    """Analyse what is the provider and choose the well component"""

    interface.implements(IAlbum)

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        url = self.context.getRemoteUrl()
        self.resource = None
        if picasa.check(url):
            self.resource = picasa.Link(context, request)
        elif flickr.check(url):
            self.resource = flickr.Link(context, request)

    def imgs(self, **kwargs):
        return self.resource.imgs(**kwargs)

    @property
    def creator(self):
        return self.resource.creator
    
    @property
    def title(self):
        return self.resource.title
