# Default Display action
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

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

class IDisplayAction(Interface):
    """
    Interface for the configurable aspects of a notify action.
    This is also used to create add and edit forms, below.
    """
         
class DisplayAction(SimpleItem):
    """The actual persistent implementation of the notify action element.
    """
    implements(IDisplayAction, IRuleElementData)
    
    element = 'paab.policy.Display'
    
    @property
    def summary(self):
        pass


class DisplayActionExecutor(object):
    """The executor for this action.
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IDisplayAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        request = self.context.REQUEST
        obj = self.event.object
        parent = obj.getParentNode()
        r = parent.title
        p = self.context
        wftool = getToolByName(p, "portal_workflow")

        id = obj.id
        title = obj.title
        description = obj.description

        _createObjectByType('Topic', obj, id=id, title= title, description=description)
        topic = getattr(obj, id) 

#            if language is not None:
#                topic.setLanguage(language)
#        type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
#        type_crit.setValue('News Item')

        sort_crit = topic.addCriterion('created','ATSortCriterion')
        state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
        state_crit.setValue('published')
        topic.setSortCriterion('effective', True)
        topic.unmarkCreationFlag()

        subject_crit =  topic.addCriterion('subject','ATListCriterion')
        subject_crit.field = u'Subject' 
        subject_crit.value = (title, )
        subject_crit.operator = u'or'

        status = wftool.getStatusOf("simple_publication_workflow", topic)
        if status['review_state'] != 'published':
            wftool.doActionFor(topic, 'publish')

        obj.setDefaultPage(id)

        return True 
        
class DisplayAddForm(AddForm):
    """An add form for notify rule actions.
    """
    form_fields = form.FormFields(IDisplayAction)
    label = _(u"Add Deafult Action")
    description = _(u"A notify action can show a message to the user.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        a = DisplayAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class DisplayEditForm(EditForm):
    """An edit form for notify rule actions.
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IDisplayAction)
    label = _(u"Edit Display Action")
    description = _(u"A display action can show a message to the user.")
    form_name = _(u"Configure element")
