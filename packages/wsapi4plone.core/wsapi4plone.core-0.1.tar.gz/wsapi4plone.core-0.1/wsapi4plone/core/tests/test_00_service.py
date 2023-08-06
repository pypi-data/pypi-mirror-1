# -*- coding: utf-8 -*-
import unittest

from zope.app.container.interfaces import IContainer
from zope.app.testing import ztapi
from zope.interface import implements, Interface

import wsapi4plone.core as wsapi4plone


class Dummy(object):
    implements(Interface)


class DummyContainer(object):
    implements(IContainer)


class TestService(unittest.TestCase):

    def setUp(self):
        ztapi.provideAdapter(Interface, wsapi4plone.IService, wsapi4plone.Service)
        dummy = Dummy()
        self.serviced_dummy = wsapi4plone.IService(dummy)

    def test_context(self):
        self.failUnlessEqual(Dummy, self.serviced_dummy.context.__class__)

    def test_get_skleton(self):
        try:
            skel = self.serviced_dummy.get_skeleton(filtr=[])
        except NotImplementedError:
            return
        self.fail("Something was returned from a method that is not implemented. returned: %s" % skel)

    def test_get_object(self):
        try:
            obj = self.serviced_dummy.get_object(attrs=[])
        except NotImplementedError:
            return
        self.fail("Something was returned from a method that is not implemented. returned: %s" % obj)

    def test_get_type(self):
        try:
            type_ = self.serviced_dummy.get_type()
        except NotImplementedError:
            return
        self.fail("Something was returned from a method that is not implemented. returned: %s" % type_)

    def test_get_misc(self):
        try:
            misc = self.serviced_dummy.get_misc(as_callback=False)
        except NotImplementedError:
            return
        self.fail("Something was returned from a method that is not implemented. returned: %s" % misc)

    def test_set_properties(self):
        try:
            props = self.serviced_dummy.set_properties(params={})
        except NotImplementedError:
            return
        self.fail("Something was returned from a method that is not implemented. returned: %s" % props)

    def test_clipboard(self):
        try:
            cb = self.serviced_dummy.clipboard(action='', target='somewhere', destination='elsewhere')
        except NotImplementedError:
            return
        self.fail("Something was returned from a method that is not implemented. returned: %s" % cb)


class TestServiceContainer(unittest.TestCase):

    def setUp(self):
        ztapi.provideAdapter(IContainer, wsapi4plone.IServiceContainer, wsapi4plone.ServiceContainer)
        dummy = DummyContainer()
        self.serviced_dummy = wsapi4plone.IServiceContainer(dummy)

    def test_create_object(self):
        try:
            obj = self.serviced_dummy.create_object(type_name='object_type', id_='object')
        except NotImplementedError:
            return
        self.fail("Something was returned from a method that is not implemented. returned: %s" % obj)

    def test_delete_object(self):
        try:
            is_deleted = self.serviced_dummy.delete_object(id_='object')
        except NotImplementedError:
            return
        self.fail("Something was returned from a method that is not implemented. returned: %s" % is_deleted)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestService))
    suite.addTest(unittest.makeSuite(TestServiceContainer))
    return suite
