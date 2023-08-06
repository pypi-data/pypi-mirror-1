from StringIO import StringIO

from zope.component import adapts, getUtility, queryAdapter
from zope.schema.interfaces import IField

from z3c.form.interfaces import NOVALUE
from z3c.form.datamanager import DataManager

from plone.namedfile.interfaces import INamedImage

from plone.app.memberschema.interfaces import IPortraitField

from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

_marker = object()

class MemberDataManager(DataManager):
    """Data manager for member properties
    """
    
    adapts(IPropertiedUser, IField)
    
    def __init__(self, data, field):
        self.user = data
        self.field = field
        self.name = field.__name__
        self.sheet = self._findPropertySheetFor(self.name)

    def get(self):
        if self.sheet is None:
            raise AttributeError(self.name)
        try:
            # This will return field.default if self.name is in the schema.
            # If it's not, it'll raise a KeyError, which here we translate
            # into an AttributeError.
            return self.sheet.getProperty(self.name)
        except KeyError:
            raise AttributeError(self.name)

    def query(self, default=NOVALUE):
        try:
            return self.get()
        except AttributeError:
            return default

    def set(self, value):
        if self.field.readonly:
            raise TypeError(u"Cannot write to read-only field %s" % self.name)
        elif not IMutablePropertySheet.providedBy(self.sheet):
            raise TypeError(u"No mutable property sheet found for %s" % self.name)
        self.sheet.setProperty(self.user, self.name, value)

    def canAccess(self):
        return self.sheet is not None

    def canWrite(self):
        return self.sheet is not None and \
                not self.field.readonly and \
                IMutablePropertySheet.providedBy(self.sheet)
        
    def _findPropertySheetFor(self, name):

        # Plone users have a method to get property sheets in order, which is
        # what we really want.
        list_sheets = getattr(self.user, 'getOrderedPropertySheets', self.user.listPropertysheets)
        for sheet in list_sheets():
            if sheet.hasProperty(name):
                return sheet
        return None

class MemberPortraitDataManager(MemberDataManager):
    """Data manager for a member porotrait
    """
    
    adapts(IPropertiedUser, IPortraitField)
    
    def __init__(self, data, field):
        super(MemberPortraitDataManager, self).__init__(data, field)
        self.userid = data.getId()

    def get(self):
        if self.sheet is None:
            raise AttributeError(u"Portrait field %s not found", self.field.__name__)
        
        portrait = self.membership.getPersonalPortrait(self.userid)
        if portrait is None:
            raise AttributeError(u"No portrait for user %s" % self.userid)
        
        named = queryAdapter(portrait, INamedImage, "portrait", _marker)
        if named is _marker:
            raise AttributeError(u"Portrait for %s not found" % self.userid)
        
        return named

    def query(self, default=NOVALUE):
        try:
            return self.get()
        except AttributeError:
            return default

    def set(self, value):
        if self.field.readonly:
            raise TypeError(u"Cannot write to read-only field %s" % self.field.__name__)
        elif not IMutablePropertySheet.providedBy(self.sheet):
            raise TypeError(u"No mutable property sheet found for %s" % self.name)
        elif not INamedImage.providedBy(value):
            raise TypeError(u"Value must be a named image")
        
        portrait = StringIO(value.data)
        portrait.filename = value.filename
        self.membership.changeMemberPortrait(portrait, self.userid)

    @property
    def membership(self):
        site = getUtility(ISiteRoot)
        return getToolByName(site, 'portal_membership')