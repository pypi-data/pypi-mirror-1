from logging import getLogger

from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from wsapi4plone.core.browser.interfaces import IQuery
from wsapi4plone.core.browser.wsapi import WSAPI
from wsapi4plone.core.interfaces import IFormatQueryResults


class Query(object):
    implements(IQuery)
    logger = getLogger(' Query ')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def query(self, filtr={}):
        """
        @param filtr - search criteria given to filter the results
        """
        catalog = getToolByName(getSite(), 'portal_catalog')
        brains = catalog(filtr)
        formatter = getUtility(IFormatQueryResults)
        self.logger.info("- query - Searching catalog with this search criteria: %s." % (filtr))
        return formatter(brains)