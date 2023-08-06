from five import grok
from plone.directives import form

from zope.i18nmessageid import MessageFactory

from zope.interface import Interface
from zope import schema

from z3c.form import button

from collective.novate.interfaces import INovateLayer

from plone.app.layout.viewlets.interfaces import IBelowContent
from plone.app.workflow.browser.sharing import SharingView

from Acquisition import aq_inner, aq_base
from AccessControl.Owned import ownerInfo, UnownableOwner

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.interfaces import IDublinCore
from Products.CMFCore.utils import getToolByName

_ = MessageFactory('collective.novate')

class NovateLink(grok.Viewlet):
    """Present a link to the novation form
    """
    
    grok.name('novate-link')
    grok.require('collective.novate.NovateOwner')
    grok.context(Interface)
    grok.layer(INovateLayer)
    grok.view(SharingView)
    grok.viewletmanager(IBelowContent)
    
    def update(self):
        pass

class INovateFields(form.Schema):
    
    form.widget(owner='plone.formwidget.autocomplete.AutocompleteFieldWidget')
    
    owner = schema.Choice(
            title=_(u"Owner"),
            description=_(u"Please choose the new owner"),
            vocabulary="plone.principalsource.Users",
        )
    
    recursive = schema.Bool(
            title=_(u"Change sub-objects"),
            description=_(u"If selected, the ownership of all sub-objects will be changed as well."),
            default=False,
        )

class Novate(form.SchemaEditForm):
    """The actual form
    """
    
    grok.name('novate')
    grok.context(Interface)
    grok.require('collective.novate.NovateOwner')
    grok.layer(INovateLayer)
    
    label = _(u"Change ownership")
    description = _(u"Please select a new owner below")
    
    schema = INovateFields
        
    def getContent(self):
        # Edit a simple dict
        return {}
    
    @button.buttonAndHandler(_(u'Change'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        object = aq_inner(self.context)
        user_id = data['owner']
        recursive = data['recursive']
        
        def fixOwner(object, owner_info):
            old_owner = object.getOwnerTuple()
            if old_owner is not UnownableOwner and old_owner != owner_info:
                object._owner = owner_info
        
        def fixOwnerRole(object, user_id):
            # Get rid of all other owners
            owners = object.users_with_local_role('Owner')
            for o in owners:
                roles = list(object.get_local_roles_for_userid(o))
                roles.remove('Owner')
                if roles:
                    object.manage_setLocalRoles(o, roles)
                else:
                    object.manage_delLocalRoles([o])
            roles = list(object.get_local_roles_for_userid(user_id))
            roles.append('Owner')
            object.manage_setLocalRoles(user_id, roles)
        
        def fixCreator(object, user_id):
            # Update Creator metadata. The first user in the list returned
            # by listCreators() is given as the Creator DC metadata
            if IDublinCore.providedBy(object):
                creators = list(object.listCreators())
                if user_id in creators:
                    creators.remove(user_id)
                creators.insert(0, user_id)
                object.setCreators(creators)
        
        # Find a user object

        membership = getToolByName(object, 'portal_membership')
        acl_users = getattr(object, 'acl_users')
        user = acl_users.getUserById(user_id)
        if user is None:
            user = membership.getMemberById(user_id)
            if user is None:
                raise KeyError('Only retrievable users in this site can be made owners.')
        
        new_owner_info = ownerInfo(user)
        if new_owner_info is None:
            raise KeyError("Invalid owner")
        
        # Change ownership

        fixOwner(object, new_owner_info)
        fixOwnerRole(object, user_id)
        fixCreator(object, user_id)
        
        if hasattr(aq_base(object), 'reindexObject'):
            object.reindexObject()

        if recursive:
            catalog_tool = getToolByName(object, 'portal_catalog')
            for brain in catalog_tool(path={'query':'/'.join(object.getPhysicalPath())}):
                obj = brain.getObject()
                fixOwner(obj, new_owner_info)
                fixOwnerRole(obj, user_id)
                fixCreator(obj, user_id)
                if hasattr(aq_base(obj), 'reindexObject'):
                    obj.reindexObject()
        
        IStatusMessage(self.request).addStatusMessage(_(u"Owner changed"), "info")
        self.request.response.redirect(self.context.absolute_url())
    
    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect(self.context.absolute_url()) 