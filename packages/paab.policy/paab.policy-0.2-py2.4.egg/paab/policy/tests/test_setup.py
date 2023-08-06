import unittest
from paab.policy.tests.base import PaabPolicyTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType 
from zope.component import getUtility, getMultiAdapter 
from plone.contentrules.rule.interfaces import IRuleAction  
from plone.contentrules.engine.interfaces import IRuleStorage 

class TestSetup(PaabPolicyTestCase):

    def test_portal_title(self):
        self.assertEquals("Paab", self.portal.getProperty('title'))
        
    def test_portal_description(self):
        self.assertEquals("Welcome to paab", self.portal.getProperty('description'))

    def test_homeTopicDefault(self):
        """test if there's a topic in home called blog and is the default's root folder's display and it's published"""
        blog = self.portal.blog
        self.assertEquals("ATTopic" , blog.meta_type)
        self.assertEquals("blog" , blog.id)
        self.assertEquals("blog" , self.portal.defaultView())

        workflowTool = getToolByName(self.portal, "portal_workflow")
        status = workflowTool.getStatusOf("simple_publication_workflow", blog)
        self.assertEquals("published" , status['review_state'])

    def test_homeCriteria(self):
        """the criteria of the collection should be just news """
        blog = self.portal.blog
        criteria = blog.crit__Type_ATPortalTypeCriterion
        self.assertEquals( u'Type'  , criteria.field )
        self.assertEquals( (u'Blog Post',)  , criteria.value )

    def test_homeNewsWorkflow(self):
        """the collection should show just published content """
        blog = self.portal.blog
        criteria = blog.crit__review_state_ATSimpleStringCriterion
        self.assertEquals( u'published'  , criteria.value )

    def test_homeNewsSortOrder(self):
        """the collection should show just published content """
        blog = self.portal.blog
        criteria = blog.crit__effective_ATSortCriterion 
        self.assertEquals( True  , criteria.reversed )
        self.assertEquals( u'effective' , criteria.field )

    def test_homeContent(self):
        """after adding silly news on home and other folder, does the collection show them"""
        self.setRoles(('Manager',))

        blog = self.portal.blog
        q1 = blog.queryCatalog(batch=True)

        # I create a news item and i publish it
        self.portal.invokeFactory("News Item", "n1", title= 'n1', description='')         
        n1 = self.portal.n1
        wftool = getToolByName(self.portal, "portal_workflow")
        status = wftool.getStatusOf("simple_publication_workflow", n1)
        if status['review_state'] != 'published':
            wftool.doActionFor(n1, 'publish', 'simple_publication_workflow')

        #is it on the collection ?
        q2 = blog.queryCatalog(batch=True)
        self.assertEquals( q1.length + 1 , q2.length )

    def test_contentRules(self):
        """here we should have 2 content rules, one for display and another for keywords"""
        self.setRoles(('Manager',))
        blog = self.portal.blog

        element = getUtility(IRuleAction, name='paab.policy.Default')
        storage = getUtility(IRuleStorage)

        # are the content rules defined ?       
        self.assertEquals( storage['rule-1'].description, 'Keyword')
        self.assertEquals( storage['rule-2'].description, 'Default folder display')

    def test_smartFolderViewEmpty(self):
        """test a view empty and if it works a default collection view"""
        pass

    def test_smartFolderViewContentTypes(self):
        """test if different content types are on the view"""
        pass

    def test_smartFolderViewComments(self):
        pass

    def test_subjectInFolder(self):
        """Here should have the folder title"""
        pass

    def test_subjectInRoot(self):
        """Here should have the plone site"""
        pass

    def test_subjectWithOtherKeys(self):
        """Here should have these other keys and no the default ones"""
        pass

    def test_folderDisplaySetup(self):
        """If i add a folder, a smart folder with title as criteria should be the default display"""
        pass
        
    def test_folderDisplayRunning(self):
        """I add a folder, i add a news and it should be as in the folder with the folder title as a keyword"""
        pass
    
    def test_blogPostDisplayTitle(self):
        """"""
        pass

    def test_blogSectionDisplayTitle(self):
        """"""
        pass

    def test_linksTitleAreNotLinksInSectionsViews(self):
        """"""
        pass

    def test_UserCannotPossibleAddDocumentes(self):
        """"""
        pass

    def test_userCannotPossibleAddCollections(self):
        """"""
        pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
