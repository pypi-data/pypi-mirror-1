from Products.Five import BrowserView
from urllib import urlencode

from collective.gallery.interfaces import IAlbum
from zope import interface

def check(url):
    return False

class Link(BrowserView):
    """Flickr implementation of IAlbum over Link content type
    please check ??
    for a complete reference of kwargs
    """
    interface.implements(IAlbum)

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        link = self.context.getRemoteUrl().split('/')
        #TODO get information from the link
 
    def imgs(self, **kwargs):
        results = []
        
        return results
