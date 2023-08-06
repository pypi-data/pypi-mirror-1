# -*- coding: utf-8 -*-
import unittest
import xmlrpclib

from zope.component import getUtility
from ZPublisher.xmlrpc import Response
from ZPublisher.tests.test_xmlrpc import FauxResponse

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase

from wsapi4plone.core.browser.query import Query
from wsapi4plone.core.interfaces import IFormatQueryResults

class TestQuery(PloneTestCase.PloneTestCase):
    """The 'query' call is basically a middle-person between the client and the
    portal_catalog (a Plone tool that stores index information). The parameters
    passed to 'query' call are in an *args and **kwargs fashion (e.g.
    portal_catalog(Title='Welcome') would translate to query({'Title':
    'Welcome'}))."""

    def test_query(self):
        resp = Response(FauxResponse())
        q = Query(self.portal, '')
        queryFormater = getUtility(IFormatQueryResults)
        portal_catalog = getToolByName(self.portal, 'portal_catalog')
        criteria = {'Type': 'Collection'}
        tool_results = queryFormater(portal_catalog(criteria))
        q_data = q.query(criteria)
        resp.setBody(q_data)
        q_body = resp._body
        q_resp, method = xmlrpclib.loads(q_body)
        q_results = q_resp[0]
        for path in q_results:
            self.failUnless(path in tool_results.keys())
            q_index = q_results[path]
            tool_index = tool_results[path]
            for i in tool_index:
                if isinstance(q_index[i], xmlrpclib.DateTime):
                    # xmlrpclib formats dates to the ISO 8601 standard.
                    self.failUnlessEqual(tool_index[i].ISO8601(), q_index[i])
                    continue
                elif isinstance(q_index[i], list):
                    # xmlrpclib converts tuples to lists.
                    q_index[i] = tuple(q_index[i])
                self.failUnlessEqual(tool_index[i], q_index[i])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQuery))
    return suite
