from collective.gallery.interfaces import IAlbum
from urllib import urlencode
from zope import interface

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

class Folder(BrowserView):
    """Plone folder implementation of IAlbum"""
    interface.implements(IAlbum)
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        creators = context.Creators()
        if creators:
            self.creator = creators[0]
        self.title = context.Title
 
    #TODO:make cache
    def imgs(self, **kwargs):
        results = []
        catalog = getToolByName(self.context, 'portal_catalog')
        kwargs['path'] = '/'.join(self.context.getPhysicalPath())
        photos = catalog.searchResults(**kwargs)

        for photo in photos:
            struct = {}
            struct['src'] = photo.getURL()
            struct['thumb_url'] = photo.getURL()
            struct['title'] = photo.Title
            struct['description'] = photo.Description
            results.append(struct)

        return results
