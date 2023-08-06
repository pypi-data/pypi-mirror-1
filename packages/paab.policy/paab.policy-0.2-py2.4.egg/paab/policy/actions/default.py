# Default Keyword action
# Based on plone's notify.py
#
from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import PloneMessageFactory
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

class IDefaultAction(Interface):
    """
    Interface for the configurable aspects of a notify action.
    This is also used to create add and edit forms, below.
    """
         
class DefaultAction(SimpleItem):
    """The actual persistent implementation of the notify action element.
    """
    implements(IDefaultAction, IRuleElementData)
    
    element = 'paab.policy.Default'
    
    @property
    def summary(self):
        pass


class DefaultActionExecutor(object):
    """The executor for this action.
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IDefaultAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        request = self.context.REQUEST
        obj = self.event.object
        parent = obj.getParentNode()
        r = parent.title
        if obj.Subject() == (): 
            obj.setSubject(r)
            obj.reindexObject()
        return True 
        
class DefaultAddForm(AddForm):
    """An add form for notify rule actions.
    """
    form_fields = form.FormFields(IDefaultAction)
    label = _(u"Add Deafult Action")
    description = _(u"A notify action can show a message to the user.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        a = DefaultAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class DefaultEditForm(EditForm):
    """An edit form for notify rule actions.
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IDefaultAction)
    label = _(u"Edit Default Action")
    description = _(u"A default action can show a message to the user.")
    form_name = _(u"Configure element")
