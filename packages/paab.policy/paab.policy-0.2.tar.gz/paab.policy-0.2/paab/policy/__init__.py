from Products.CMFCore.DirectoryView import registerDirectory
GLOBALS = globals()
registerDirectory('skins', GLOBALS)

# Monkey patching to add a computed field for comments
import logging
from Products.Archetypes.atapi import *
from Products.Archetypes.ClassGen import generateMethods
from Products.Archetypes.public import listTypes
from Products.Archetypes.Schema import Schema
from Products.Archetypes.BaseContent import BaseContent
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName 

logger = logging.getLogger('Adding computed field')


def howManyReplies(self, context):
    urltool = getToolByName(context, "portal_url") 
    query = {'path' : '/'.join(context.getPhysicalPath()), 'portal_type': 'Discussion Item'}
    discusion = context.portal_catalog.searchResults(query)
    return(len(discusion))


def addExtraField(context):

    types_to_patch = ['ATDocument','ATNewsItem','ATLink','ATEvent','ATImage']

    my_schema = ( 
    ComputedField(
        name='replies',
        expression='(context.howManyReplies(context))',
        widget=ComputedWidget(
            visible={'view':'visible', 'edit':'invisible'},
            label='Comments',
            label_msgid='BRFieldsAndWidgets_label_Endereco',
            i18n_domain='BRFieldsAndWidgets',
        ),
        default_output_type='text/x-html-safe',
        ),
        )

    contentTypes = listTypes('ATContentTypes')
    contentTypeClasses = [ct['klass'] for ct in contentTypes if ct['name'] in types_to_patch]
    #contentTypeClasses.append(BaseContent)

    for klass in contentTypeClasses:
        schema = getattr(klass, 'schema', None)
        for i in my_schema:
            fieldName = i.getName()
            try:
                fieldCopy = i.copy()
                schema[fieldName] = fieldCopy
                schema.moveField(fieldName, pos='bottom')
                generateMethods(klass, [fieldCopy])
                schema[fieldName].widget.macro = 'keywords-widget'
                klass.howManyReplies = howManyReplies 

            except Exception, e:
                logger.info('unable to install field "%s" into class %s: %s'
                                   % (fieldName, klass, str(e)))

    try:
        if 'getMyKeywords' not in catalog.indexes():
            portal = context.getSite()
            catalog = portal.portal_catalog
            catalog.addIndex('getMyKeywords', 'KeywordIndex')
    except:
        pass


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
   
    # i should use annotations 
    addExtraField(context)    
