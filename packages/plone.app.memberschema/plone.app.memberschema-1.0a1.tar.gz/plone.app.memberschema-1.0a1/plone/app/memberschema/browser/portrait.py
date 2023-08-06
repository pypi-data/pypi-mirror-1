from zope.component import adapter
from zope.interface import implementer

from z3c.form.interfaces import IFieldWidget, IFormLayer
from z3c.form.widget import FieldWidget

from plone.formwidget.namedfile.widget import NamedImageWidget

from plone.app.memberschema.interfaces import IPortraitField

from Products.CMFCore.utils import getToolByName

class PortraitWidget(NamedImageWidget):
    """Custom widget for portrait fields that displays the correct download
    URL. Actual getting and setting of the portrait image is managed via the
    custom datamanager in datamanager.py.
    """
    
    @property
    def download_url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        membership = getToolByName(self.context, 'portal_membership')
        userid = membership.getAuthenticatedMember().getId()
        return u"%s/portal_memberdata/portraits/%s" % (portal_url, userid)

@implementer(IFieldWidget)
@adapter(IPortraitField, IFormLayer)
def PortraitFieldWidget(field, request):
    return FieldWidget(field, PortraitWidget(request))