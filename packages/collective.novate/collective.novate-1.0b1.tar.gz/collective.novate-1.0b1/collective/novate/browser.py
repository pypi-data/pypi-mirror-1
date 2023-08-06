from five import grok
from plone.directives import form

from zope.i18nmessageid import MessageFactory

from zope.interface import Interface
from zope import schema

from z3c.form import button

from collective.novate.interfaces import INovateLayer

from plone.app.layout.viewlets.interfaces import IBelowContent
from plone.app.workflow.browser.sharing import SharingView

from Acquisition import aq_inner
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
        
        context = aq_inner(self.context)
        owner = data['owner']
        
        # Update Creator metadata. The first user in the list returned
        # by listCreators() is given as the Creator DC metadata
        if IDublinCore.providedBy(context):
            creators = list(context.listCreators())
            if owner in creators:
                creators.remove()
            creators.insert(0, owner)
            context.setCreators(creators)
        
        plone_utils = getToolByName(context, 'plone_utils')
        plone_utils.changeOwnershipOf(context, owner, recursive=data['recursive'])
        
        IStatusMessage(self.request).addStatusMessage(_(u"Owner changed"), "info")
        self.request.response.redirect(self.context.absolute_url())
    
    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect(self.context.absolute_url()) 