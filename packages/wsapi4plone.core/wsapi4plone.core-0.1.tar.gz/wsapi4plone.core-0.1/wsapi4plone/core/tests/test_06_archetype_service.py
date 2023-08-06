# -*- coding: utf-8 -*-
import unittest
import xmlrpclib

from zope.app.testing import ztapi
from zope.interface import Interface

from DateTime import DateTime
from Products.Archetypes.interfaces import IBaseFolder, IBaseObject
from Products.ATContentTypes.interface.topic import IATTopic
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

import wsapi4plone.core as wsapi4plone

@onsetup
def setup():
    zcml.load_config('configure.zcml', wsapi4plone.tests)
    ztapi.provideAdapter(IBaseObject, wsapi4plone.IService, wsapi4plone.ATObjectService)
    ztapi.provideAdapter(IBaseFolder, wsapi4plone.IServiceContainer, wsapi4plone.ATFolderService)

setup()
PloneTestCase.setupPloneSite()


class TestATObjectService(PloneTestCase.PloneTestCase):
    # The wsapi4plone.services.archetype_service.ATObjectService does not
    # need tested unless functionality is added to it. Its base class has
    # been tested in test_01_plone_service.
    pass


class TestATFolderService(PloneTestCase.PloneTestCase):
    # The wsapi4plone.services.archetype_service.ATFolderService does not
    # need tested unless functionality is added to it. Its base class has
    # been tested in test_01_plone_service.
    pass


class TestATTopicService(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # Provide the Topic Service adapter.
        ztapi.provideAdapter(IATTopic, wsapi4plone.IServiceContainer,
                             wsapi4plone.services.archetype_service.ATTopicService)
        self.login('test_user_1_')
        # Create two Events (event1 and event2) for use in the Collection.
        event1 = self.folder.invokeFactory('Event', 'event1',
                                           title="Event One",
                                           start_date="2009-01-01",
                                           end_date="2012-12-21",
                                           event_url="http://weblion.psu.edu/",
                                           location="University Park, Pennsylvania, United States of America")
        self.event1 = getattr(self.folder, event1)
        event2 = self.folder.invokeFactory('Event', 'event2',
                                           title="Event Two",
                                           start_date="2008-09-01",
                                           end_date="2009-05-13",
                                           event_url="http://weblion.psu.edu/",
                                           location="University Park, Pennsylvania, United States of America")
        self.event2 = getattr(self.folder, event2)
        self.loginAsPortalOwner()
        # Create a Collection.
        collect1 = self.portal.invokeFactory('Topic', 'collect1', title="Collection One")
        self.collect1 = getattr(self.portal, collect1)
        # Create a Type criteria.
        self.criteria = self.collect1.addCriterion('Type', 'ATSelectionCriterion')
        self.criteria.setValue('Event')
        self.logout()

    def test_get_misc(self):
        self.login('test_user_1_')
        serviced_collect1 = wsapi4plone.IService(self.collect1)
        actual_results = serviced_collect1.get_misc()
        self.logout()
        # Check for the collection content results.
        accepted_paths = (u'/'.join(self.event1.getPhysicalPath()),
                          u'/'.join(self.event2.getPhysicalPath()),)
        for path in actual_results['contents']:
            if path not in accepted_paths:
                self.fail("Could not find %s in the list of expected paths." % path)
        # Check for the criteria results.
        self.failUnless(actual_results['criteria'].get(self.criteria.id, False))
        actual_criteria = actual_results['criteria'][self.criteria.id]
        for attr in actual_criteria:
            self.failUnlessEqual(actual_criteria[attr]['value'], self.criteria[attr])

    def test_get_misc_as_callback(self):
        self.login('test_user_1_')
        serviced_collect1 = wsapi4plone.IService(self.collect1)
        actual_results = serviced_collect1.get_misc(as_callback=True)
        self.logout()
        # Check for the collection content results as a callback.
        callback = actual_results['contents.callback']
        # The call back should always have a function and args
        self.failUnless(callback.get('args', False) and callback.get('function', False))
        # The query criteria should look like the compiled query from the collection.
        self.failUnlessEqual(callback['args'][0], self.collect1.buildQuery())
        self.failUnlessEqual(callback['function'], 'query')


def test_suite():
    suite = unittest.TestSuite()
    # suite.addTest(unittest.makeSuite(TestATObjectService))
    # suite.addTest(unittest.makeSuite(TestATFolderService))
    suite.addTest(unittest.makeSuite(TestATTopicService))
    return suite