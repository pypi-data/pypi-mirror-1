# -*- coding: utf-8 -*-
import os
import unittest
import xmlrpclib

from zope.app.testing import ztapi
from zope.interface import Interface

from DateTime import DateTime
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

import wsapi4plone.core as wsapi4plone
from expected_results import MEMBERS_SKELETON, MEMBERS_VALUES, MEMBERS_TYPE, MEMBERS_CHANGES, IMAGE1, PORTAL_SKELETON, PORTAL_VALUES

@onsetup
def setup():
    zcml.load_config('configure.zcml', wsapi4plone.tests)
    ztapi.provideAdapter(Interface, wsapi4plone.IService, wsapi4plone.PloneService)
    ztapi.provideAdapter(Interface, wsapi4plone.IServiceContainer, wsapi4plone.PloneServiceContainer)

setup()
PloneTestCase.setupPloneSite()


class TestPloneService(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        grouptool = self.portal.portal_groups
        administratorsGroup = grouptool.getGroupById("Administrators")
        administratorsGroup.addMember("test_user_1_")
        self.logout()

    def test_context(self):
        context = wsapi4plone.IServiceContainer(self.folder).context
        self.failUnlessEqual(context.__class__.__name__, 'ATFolder')

    def test_get_skeleton(self):
        members_skel = wsapi4plone.IService(self.portal.Members).get_skeleton()
        self.failUnlessEqual(MEMBERS_SKELETON, members_skel)

    def test_get_object(self):
        # We need to login to get the values of some of the attributes (e.g. locallyAllowedTypes).
        self.login('test_user_1_')
        members_obj = wsapi4plone.IService(self.portal.Members).get_object()
        self.logout()
        actual = members_obj
        expected = MEMBERS_VALUES
        actual_keys = actual.keys()
        expected_keys = expected.keys()
        # Check the keys for any differences before moving on.
        self.failUnlessEqual(set(actual_keys), set(expected_keys),
                             "Difference attributes were discovered. The \
                             differening attribute(s) are %s." % \
                             list(set(actual_keys).difference(set(expected_keys))))
        # Check each attribute's value individually since list order and
        # DateTime values will not be the same.
        for attr in actual:
            if isinstance(expected[attr], DateTime):
                # It is good enough that they are the same type,
                # since the expected results do not have the most current date and time.
                continue
            elif isinstance(expected[attr], list):
                # We need to take a closer look at lists since they are
                # ordered, because there is no guaranty that the results will
                # be in the same order.
                expected_value = expected[attr]
                resulting_value = actual[attr]
                self.failUnlessEqual(set(resulting_value), set(expected_value),
                                     "Difference attributes were discovered. \
                                     The differening attribute(s) are %s." % \
                                     list(set(resulting_value).difference(set(expected_value))))
                continue
            # If it gets this far, it must be a base type or it will fail.
            self.failUnlessEqual(expected[attr], actual[attr])

    def test_get_type(self):
        type_ = wsapi4plone.IService(self.portal.Members).get_type()
        self.failUnlessEqual(type_, MEMBERS_TYPE)

    def test_get_misc(self):
        # The get_misc should return None for the generic serviced object.
        # get_misc is used for special use-cases (e.g. the contents of a Collection)
        # to provide additional data that is not part of the schema.
        misc = wsapi4plone.IService(self.portal.Members).get_misc()
        self.failIf(misc, "%s was returned by get_misc, for a general wsapi4plone.Service adaptation." % misc)

    def test_set_properties(self):
        obj = wsapi4plone.IService(self.portal.Members)
        self.login('test_user_1_')
        nata = obj.set_properties(MEMBERS_CHANGES)
        self.logout()
        # Check the object for the changes.
        for attr in MEMBERS_CHANGES:
            self.failUnlessEqual(self.portal.Members[attr], MEMBERS_CHANGES[attr])

    def test_clipboard(self):
        self.fail("This is not implmented yet, therefore it is suppose to fail.")

    def test_with_binary_data(self):
        # Grab some sample data.
        os.chdir(wsapi4plone.__path__[0])
        data = open(os.path.join('tests', 'image.png')).read()
        # Create an Image object at image1.
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Image', 'image1', image=data)
        self.logout()
        # Login and get the object from the Service point-of-view.
        self.login('test_user_1_')
        img = wsapi4plone.IService(self.portal.image1).get_object(['image'])
        self.logout()
        # Examin that everything is as expected.
        for attr in img['image']:
            if attr == 'data':
                self.failUnlessEqual(img['image'][attr], data)
                continue
            self.failUnlessEqual(img['image'][attr],
                                 IMAGE1['image'][attr])

    def test_set_binary_data(self):
        # Grab some sample data.
        os.chdir(wsapi4plone.__path__[0])
        data = open(os.path.join('tests', 'image.png')).read()
        # Create an Image object at image1.
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Image', 'image1', image=data)
        self.logout()
        # Login and get the object from the Service point-of-view.
        self.login('test_user_1_')
        result = wsapi4plone.IService(self.portal.image1).set_properties({'image': xmlrpclib.Binary(data)})
        self.logout()
        # Check that the data was set.
        self.failUnlessEqual(self.portal.image1['image'].data, data)


class TestPloneServiceContainer(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.obj = wsapi4plone.IServiceContainer(self.folder)

    def _put_image_in_folder(self):
        return self.folder.invokeFactory('Image', 'image4')

    def test_context(self):
        context = wsapi4plone.IServiceContainer(self.folder).context
        self.failUnlessEqual(context.__class__.__name__, 'ATFolder')

    def test_create_object(self):
        self.login('test_user_1_')
        id_ = self.obj.create_object(type_name='Image', id_='image1')
        self.logout()
        # Check to see if image1 exists.
        self.failUnless(self.folder.get(id_))

    def test_delete_object(self):
        self.login('test_user_1_')
        id_ = self._put_image_in_folder()
        deleted = self.obj.delete_object(id_=id_)
        self.logout()
        # Check to see if image1 exists.
        self.failIf(self.folder.get(id_, None))

    def test_get_misc(self):
        id_ = self._put_image_in_folder()
        misc = self.obj.get_misc()
        # ugh...
        self.failUnless(u'/plone/Members/test_user_1_/image4' in misc['contents'], "Failed to get the contents of the folder.")


class TestPloneRootService(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        ztapi.provideAdapter(IPloneSiteRoot,
                             wsapi4plone.IServiceContainer,
                             wsapi4plone.services.plone_service.PloneRootService)

    def test_get_skeleton(self):
        skel = wsapi4plone.IService(self.portal).get_skeleton()
        self.failUnlessEqual(skel, PORTAL_SKELETON)

    def test_get_object(self):
        # We need to login to get the values of some of the attributes (e.g. locallyAllowedTypes).
        self.login('test_user_1_')
        portal = wsapi4plone.IService(self.portal).get_object()
        self.logout()
        actual = portal
        expected = PORTAL_VALUES
        actual_keys = actual.keys()
        expected_keys = expected.keys()
        # Check the keys for any differences before moving on.
        self.failUnlessEqual(set(actual_keys), set(expected_keys),
                             "Difference attributes were discovered. The \
                             differening attribute(s) are %s." % \
                             list(set(actual_keys).difference(set(expected_keys))))
        # Check each attribute's value individually since list order and
        # DateTime values will not be the same.
        for attr in actual:
            if isinstance(expected[attr], DateTime):
                # It is good enough that they are the same type,
                # since the expected results do not have the most current date and time.
                continue
            elif isinstance(expected[attr], list):
                # We need to take a closer look at lists since they are
                # ordered, because there is no guaranty that the results will
                # be in the same order.
                expected_value = expected[attr]
                resulting_value = actual[attr]
                self.failUnlessEqual(set(resulting_value), set(expected_value),
                                     "Difference attributes were discovered. \
                                     The differening attribute(s) are %s." % \
                                     list(set(resulting_value).difference(set(expected_value))))
                continue
            # If it gets this far, it must be a base type or it will fail.
            self.failUnlessEqual(expected[attr], actual[attr])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPloneService))
    suite.addTest(unittest.makeSuite(TestPloneServiceContainer))
    suite.addTest(unittest.makeSuite(TestPloneRootService))
    return suite
