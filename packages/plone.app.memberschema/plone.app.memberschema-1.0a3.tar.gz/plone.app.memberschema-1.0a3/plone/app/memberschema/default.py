from zope.interface import Interface, alsoProvides
from zope import schema

from plone.namedfile.field import NamedImage
from plone.app.memberschema.interfaces import IPortraitField

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.app.memberschema')

class Basics(Interface):
    __doc__ = _(u"Basic member settings")

    fullname = schema.TextLine(
            title=_(u"Full Name"),
        )
    
    email = schema.ASCIILine(
            title=_(u"Email"),
        )

class Location(Interface):
    __doc__ = _(u"Geographic information")
    
    location = schema.TextLine(
            title=_(u"Location"),
            description=_(u"Your location - either city and country - or in a "
                           "company setting, where your office is located."),
            required=False,
        )
    
    language = schema.Choice(
            title=_(u"Language"),
            description=_(u"Your preferred language."),
            required=False,
            vocabulary='plone.app.vocabularies.AvailableContentLanguages',
            missing_value='',
        )

class Details(Interface):
    __doc__ = _(u"Further personal details")
    
    portrait = NamedImage(
            title=_(u"Portrait"),
            description=_(u"Your picture. This will be resized as necessary."),
            required=False,
        )
    
    biography = schema.Text(
            title=_(u"Biography"),
            description=_(u"A short overview of who you are and what you do. "
                           "Will be displayed on the your author page, linked "
                           "from the items you create."),
            required=False,
        )
                             
    home_page = schema.URI(
            title=_(u"Home Page"),
            description=_(u"The URL for your external home page, if you have one."),
            required = False,
            missing_value='',
        )

alsoProvides(Details[u'portrait'], IPortraitField)

class Settings(Interface):
    __doc__ = _(u"Personal settings")
        
    ext_editor = schema.Bool(
            title=_(u"Enable external editing"),
            description=_(u"When checked, an icon will be made visible on each "
                           "page which allows you to edit content with your "
                           "favorite editor instead of using browser-based editors. "
                           "This requires an additional application called ExternalEditor "
                           "installed client-side. Ask your administrator for more "
                           "information if needed."),
            required=False,
        )
        
    listed = schema.Bool(
            title=_(u"Listed in searches"),
            description=_(u"Determines if your user name is listed in user ",
                           "searches done on this site."),
            required=False,
        )