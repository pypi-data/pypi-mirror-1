from zope import interface
from zope import schema
from collective.gallery import _

class IAlbum(interface.Interface):
    """An album is a set of photo with classic dublin core"""

    title = schema.TextLine(title=_(u"Title"))

    creator = schema.TextLine(title=_(u"Author"))

    description = schema.TextLine(title=_(u"Description"))
    
    date = schema.Date(title=_(u"Date"))

    def photos(**kwargs):
        """Return the set of photos. kwargs are passed to the underline
        services used
        """
