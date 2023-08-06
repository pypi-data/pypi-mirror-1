from z3c.form import form, button

from plone.z3cform.layout import FormWrapper
from plone.autoform.form import AutoExtensibleForm

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from plone.memoize.instance import memoize

from plone.app.memberschema.interfaces import PLUGIN_NAME

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.app.memberschema')

class BaseWrapper(FormWrapper):
    
    def __init__(self, context, request):
        super(BaseWrapper, self).__init__(context, request)
        self.request['disable_border'] = True

class EditProfileForm(AutoExtensibleForm, form.EditForm):
    """Edit a particular member's profile. The member id should be given
    as the 'id' query string parameter.
    """
    
    label = _(u"Edit profile")
    
    ignorePrefix = True
    autoGroups = True
    
    pluginId = PLUGIN_NAME
    
    # Schema setup
    
    @property
    def schema(self):
        return self.getSchemata()[0]
        
    @property
    def additional_schemata(self):
        return self.getSchemata()[1:]
    
    # Data setup
    
    def getContent(self):
        membership = getToolByName(self.context, 'portal_membership')
        memberId = self.request.get('id')
        return membership.getMemberById(memberId).getUser()
        
    # Buttons
    
    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), "info")
        self.request.response.redirect(self.context.absolute_url())
    
    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect(self.context.absolute_url()) 
    
    def updateActions(self):
        super(EditProfileForm, self).updateActions()
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")
    
    # Helpers
    
    @memoize
    def getUserFolder(self):
        return getToolByName(self.context, 'acl_users')

    @memoize
    def getSchemata(self):
        plugin = getattr(self.getUserFolder(), self.pluginId)
        return plugin.getSchemata() 

class EditProfileView(BaseWrapper):
    form = EditProfileForm

class MyProfileForm(EditProfileForm):
    """Edit current user's profile
    """
    
    label = _(u"Edit profile")
    
    def getContent(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.getAuthenticatedMember().getUser()
        
class MyProfileView(BaseWrapper):
    form = MyProfileForm