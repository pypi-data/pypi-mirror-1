from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

from plone.app.portlets import utils

from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.nextprev"""

    def afterSetUp(self):
        ZopeTestCase.installPackage('collective.nextprev')

        self.loginAsPortalOwner()

        self.portal.portal_workflow.doActionFor(
            self.folder, 'publish')

        self.folder.invokeFactory(
            type_name='Topic', id='foo-topic-title',
            title='Foo Topic Title')
        topic = self.folder['foo-topic-title']
        topic.addCriterion('Type', 'ATPortalTypeCriterion'
                           ).setValue('News Item')
        topic.setSortCriterion('effective', True)
        self.portal.portal_workflow.doActionFor(topic, 'publish')

        self.login()

        self.folder.setDefaultPage('foo-topic-title')
        self.folder.setNextPreviousEnabled(True)

        self.folder.invokeFactory(
            type_name='News Item', id='foo-news-item-title',
            title='Foo News Item Title')
        self.folder.invokeFactory(
            type_name='Document', id='bar-page-title',
            title='Bar Page Title')
        self.folder.invokeFactory(
            type_name='News Item', id='baz-news-item-title',
            title='Baz News Item Title')
        self.folder.invokeFactory(
            type_name='News Item', id='qux-baz-news-item-title',
            title='Qux Baz News Item Title')

        self.loginAsPortalOwner()

        self.portal.portal_workflow.doActionFor(
            self.folder['foo-news-item-title'], 'publish')
        self.portal.portal_workflow.doActionFor(
            self.folder['bar-page-title'], 'publish')
        self.portal.portal_workflow.doActionFor(
            self.folder['baz-news-item-title'], 'publish')
        self.portal.portal_workflow.doActionFor(
            self.folder['qux-baz-news-item-title'], 'publish')

        # Create a news item in the news large folder
        self.portal.news.invokeFactory(
            type_name='News Item', id='blah-news-item-title',
            title='Blah News Item Title')
        self.portal.portal_workflow.doActionFor(
            self.portal.news['blah-news-item-title'], 'publish')

        # clear the portlets showing items
        mapping = utils.assignment_mapping_from_key(
            self.portal, "plone.leftcolumn", "context", "/")
        del mapping['navigation']
        mapping = utils.assignment_mapping_from_key(
            self.portal, "plone.rightcolumn", "context", "/")
        del mapping['news']

        self.logout()

layer = Layer([tcl_ptc.ptc_layer])
