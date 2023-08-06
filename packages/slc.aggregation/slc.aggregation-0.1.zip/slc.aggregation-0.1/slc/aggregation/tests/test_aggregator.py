from zope import component 
from zope.annotation.interfaces import IAnnotations
from zope.publisher.browser import TestRequest

from Products.CMFCore.utils import getToolByName

from p4a.subtyper.interfaces import ISubtyper

from slc.aggregation.tests.base import AggregationTestCase


class TestAggregator(AggregationTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'slave')
        slave = self.portal._getOb('slave')

        subtyper = component.getUtility(ISubtyper)
        subtyper.change_type(slave, 'slc.aggregation.aggregator')

        annotations = IAnnotations(slave)
        annotations['content_types'] = ['News Item']
        annotations['review_state'] =  ['published']
        annotations['aggregation_sources'] =  ['/master-1', '/master-2']
        annotations['keyword_list'] = []

        workflowTool = getToolByName(self.portal, "portal_workflow")
        self.portal.invokeFactory('Folder', 'master-1')
        master_1 = self.portal._getOb('master-1')
        for i in range(0, 20):  
            master_1.invokeFactory('News Item', 'news-item-%s' % i)
            item = master_1._getOb('news-item-%s' % i)
            if i < 10:
                item.setSubject(['filter_keyword'])
                workflowTool.doActionFor(item, 'publish')

            item.reindexObject()

        self.portal.invokeFactory('Folder', 'master-2')
        master_2 = self.portal._getOb('master-2')
        for i in range(0, 10):  
            master_2.invokeFactory('News Item', 'news-item-%s' % i)


    def test_is_subtyped_as_aggregator(self):
        slave = self.portal._getOb('slave')

        request = TestRequest()
        view = component.getMultiAdapter((slave, request), name="aggregator_view")

        self.assertEquals(view.is_subtyped_as_aggregator(), True)

        subtyper = component.getUtility(ISubtyper)
        subtyper.remove_type(slave)

        self.assertEquals(view.is_subtyped_as_aggregator(), False)


    def test_query_items(self):
        slave = self.portal._getOb('slave')
        request = TestRequest()
        view = component.getMultiAdapter((slave, request), name="aggregator_view")
        self.assertEquals(len(view.query_items()),  10)

        annotations = IAnnotations(slave)
        annotations['review_state'] =  ['published', 'private']
        self.assertEquals(len(view.query_items()),  30)

        annotations['aggregation_sources'] =  ['/master-1']
        self.assertEquals(len(view.query_items()),  20)

        annotations['content_types'] = ['Event']
        self.assertEquals(len(view.query_items()),  0)

        annotations['content_types'] = []
        # 11 because the parent folder is also included.
        self.assertEquals(len(view.query_items()),  21)

        annotations['content_types'] = []
        annotations['keyword_list'] = ['filter_keyword']
        annotations['aggregation_sources'] =  ['/master-1', '/master-2']
        self.assertEquals(len(view.query_items()),  10)

        annotations['review_state'] =  []
        self.assertEquals(len(view.query_items()),  10)

        annotations['keyword_list'] = ['non-existing_keyword']
        self.assertEquals(len(view.query_items()),  0)


    def test_translated_querying(self):
        """ Test that querying still works as expected with translated master
            and slave folders.
        """
        slave = self.portal._getOb('slave')

        annotations = IAnnotations(slave)
        annotations['content_types'] = ['News Item']
        annotations['review_state'] =  ['published']
        annotations['aggregation_sources'] =  ['/master-1', '/master-2']
        annotations['keyword_list'] = []

        sklave = slave.addTranslation('de')

        request = TestRequest()
        view = component.getMultiAdapter((sklave, request), name="aggregator_view")

        # Our german slave folder must only fetch german objects, of which none
        # currently exist.
        self.assertEquals(len(view.query_items()),  0)

        workflowTool = getToolByName(self.portal, "portal_workflow")
        master_1 = self.portal._getOb('master-1')
        for i in range(0, 20):  
            item = master_1._getOb('news-item-%s' % i)
            einheit = item.addTranslation('de')
            workflowTool.doActionFor(einheit, 'publish')
            einheit.reindexObject()

        self.assertEquals(len(view.query_items()),  20)

        meister_1 = master_1.addTranslation('de')
        self.assertEquals(len(meister_1.objectIds()), 20)
        self.assertEquals(len(view.query_items()),  20)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAggregator))
    return suite

