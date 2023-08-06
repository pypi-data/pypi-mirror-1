from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import locales, LoadLocaleError

def setupPortalContent(context):
        """
        Import default plone content
        """
        p = context.getSite()

        existing = p.objectIds()        
        wftool = getToolByName(p, "portal_workflow")

        # Figure out the current user preferred language
        language = None
        locale = None
        request = getattr(p, 'REQUEST', None)

        if request is not None:
            pl = IUserPreferredLanguages(request)
            if pl is not None:
                languages = pl.getPreferredLanguages()
                for httplang in languages:
                    parts = (httplang.split('-') + [None, None])[:3]
                    try:
                        locale = locales.getLocale(*parts)
                        break
                    except LoadLocaleError:
                        # Just try the next combination
                        pass
                if len(languages) > 0:
                    language = languages[0]

        # Blog topic
        if 'blog' not in existing:
            _createObjectByType('Topic', p, id='blog',
                                title= 'blog', description='')


            topic = p.blog
            if language is not None:
                topic.setLanguage(language)

            type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
            type_crit.setValue('Blog Post')
            sort_crit = topic.addCriterion('created','ATSortCriterion')
            state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
            state_crit.setValue('published')
            topic.setSortCriterion('effective', True)
            topic.unmarkCreationFlag()

            # it didn't work but it should!
            status = wftool.getStatusOf("simple_publication_workflow", topic)
            if status['review_state'] != 'published':
                wftool.doActionFor(topic, 'publish')


# Based on Clouseau code
# http://dev.plone.org/collective/browser/Clouseau 
#
# Author: Andy McKay - Licence: GPL
# Adaptation to paab: Roberto Allende
#
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal

layer_name = "paab_policy"
layer_location = "paab.policy:skins/paab_policy"

def installSkin(context):
    """ Install this product """
    out = []
    p = context.getSite()
    skinsTool = getToolByName(p, 'portal_skins')

    # add in the directory view pointing to our skin
    if layer_name not in skinsTool.objectIds():
        createDirectoryView(skinsTool, layer_location, layer_name)
        out.append('Added "%s" directory view to portal_skins' % layer_name)

    # add in the layer to all our skins    
    skins = skinsTool.getSkinSelections()
    for skin in skins:
        path = skinsTool.getSkinPath(skin)
        path = [ p.strip() for p in path.split(',') ]
        if layer_name not in path:
            path.insert(path.index('custom')+1, layer_name)

            path = ", ".join(path)
            skinsTool.addSkinSelection(skin, path)
            out.append('Added "%s" to "%s" skins' % (layer_name, skin))
        else:
            out.append('Skipping "%s" skin' % skin)

# InstallRules setup content rules
# should use generic setup in Plone 3.1+
from zope.component import getUtility, getMultiAdapter 
from plone.contentrules.rule.interfaces import IRuleAction  
from plone.contentrules.engine.interfaces import IRuleStorage 
from plone.app.contentrules.rule import Rule 
from zope.app.container.interfaces import IObjectAddedEvent
from paab.policy.actions.default import DefaultAction 
from paab.policy.actions.display import DisplayAction 
from plone.app.contentrules.conditions.portaltype import PortalTypeCondition
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.contentrules.engine.assignments import RuleAssignment
from plone.app.contentrules.rule import get_assignments 

def installRules(context):
    element = getUtility(IRuleAction, name='paab.policy.Default')
    storage = getUtility(IRuleStorage)
    portal = context.getSite()
    assignable = IRuleAssignmentManager(portal)

    rules = []
    rules.append({})
    rules[0]['name'] = 'rule-' + str( len(storage.items()) + 1 ) 
    rules[0]['title'] = 'Keyword'
    rules[0]['description'] = 'Keyword'
    rules[0]['types'] = set ( ['Document', 'News Item'] )
    rules[0]['event'] = IObjectAddedEvent
    rules[0]['action'] = DefaultAction() 
    # TODO: check if the content rule already there ?

    rules.append({})
    rules[1]['name'] = 'rule-' + str( len(storage.items()) + 2 ) 
    rules[1]['title'] = 'Display'
    rules[1]['description'] = 'Default folder display'
    rules[1]['types'] = ['Folder']
    rules[1]['event'] = IObjectAddedEvent
    rules[1]['action'] = DisplayAction() 
    # TODO: check if the content rule already there ?
   
    for r in rules:
        # Defining rule
        rule = Rule() 
        rule.title = r['name']
        rule.description = r['description']
#        rule.id = r['name']
        rule.event = r['event']
        rule.actions.append(r['action']) 
        pc = PortalTypeCondition() 
        pc.check_types = r['types']
        rule.conditions.append(pc)
        storage[r['name']] = rule

        #Asigning rule
        path = '/'.join(portal.getPhysicalPath())    
        assignable[r['name']] = RuleAssignment(r['name'])
        get_assignments(storage[r['name']]).insert(path) 
    
        # enabling the rule to subfolders 
        assignment = assignable.get(r['name'], None)
        if assignment is not None:
            assignment.bubbles = True

