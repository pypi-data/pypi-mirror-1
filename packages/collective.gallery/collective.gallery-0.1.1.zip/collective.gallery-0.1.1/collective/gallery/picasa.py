from Products.Five import BrowserView

#from picasa getting started
import gdata.photos.service
import gdata.media
import gdata.geo

import urllib
import urlparse
from urllib import urlencode

from collective.gallery.interfaces import IAlbum

from zope import interface

def check(url):
    """Ex: http://picasaweb.google.fr/ceronjeanpierre/PhotosTriEsDuMariage#
    """
    return url.startswith("http://picasaweb.google")

class Link(BrowserView):
    """Picasa implements of IAlbum over Link content type
    please check http://code.google.com/intl/fr/apis/picasaweb/docs/1.0/reference.html
    for a complete reference of kwargs
    """
    interface.implements(IAlbum)

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        url_parsed = urlparse.urlparse(self.context.getRemoteUrl())
        #('http', 'picasaweb.google.fr', '/toutpt/20091116ConcertDeRammstein', '', 'authkey=Gv1sRgCN2i5uaeazeaze', '')
        self.creator = url_parsed[2].split('/')[1]
        #plone remove the trailing # of picasa itself
        self.title = url_parsed[2].split('/')[2]
 
    #TODO:make cache
    def imgs(self, **kwargs):
        results = []
        gd_client = gdata.photos.service.PhotosService()

        albums = gd_client.GetUserFeed(user=self.creator)

        kwargs['kind'] = 'photo'
        url = '/data/feed/api/user/%s/album/%s?'%(self.creator, self.title)
        url += urlencode(kwargs)
        photos = gd_client.GetFeed(url)

        for photo in photos.entry:
            struct = {}
            struct['src'] = photo.content.src
            struct['thumb_url'] = photo.media.thumbnail[0].url
            struct['title'] = photo.title.text
            struct['description'] = photo.summary.text or ''
            results.append(struct)

        return results

class SlideShow(Link):
    def slideshow(self, width="600", height="400", **kwargs):
        """Return slideshow html embed code to use picasa slideshow flash 
        from Link Plone content type
        """
        
        BASE = """<embed type="application/x-shockwave-flash" src="http://picasaweb.google.com/s/c/bin/slideshow.swf" width="%(width)s" height="%(height)s" flashvars="%(flashvars)s" pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>"""

        flashvars = {}
        flashvars['host'] = 'picasaweb.google.com'
        flashvars['captions'] = '1'
        flashvars['feat'] = 'flashalbum'
#        flashvars['hl'] = 'fr'
        flashvars['RGB'] = '0x000000'

        feed = {}
        feed['alt'] = 'rss'
        feed['kind'] = 'photo'
        remote_parsed = urlparse.urlparse(self.context.getRemoteUrl())

        if 'authkey' in remote_parsed[4]:
            feed['authkey'] = remote_parsed[4].split('=')[1]
        feed_url = 'http://picasaweb.google.com/data/feed/api/user/%s/album/%s?'%(self.creator, self.title)
        feed_url += urlencode(feed)
        flashvars['feed'] = feed_url
        return BASE%{'width':width, 'height': height, 'flashvars':urlencode(flashvars)}
