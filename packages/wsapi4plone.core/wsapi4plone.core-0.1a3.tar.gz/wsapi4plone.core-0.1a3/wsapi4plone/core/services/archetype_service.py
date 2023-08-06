import xmlrpclib

from DateTime import DateTime
from OFS.Image import File
from zope.component import adapts, getUtility
from zope.interface import implements

from Products.ATContentTypes.interface.topic import IATTopic
from Products.Archetypes.BaseUnit import BaseUnit
from Products.Archetypes.interfaces import IBaseFolder, IBaseObject

# from interfaces import IService, IServiceContainer
from wsapi4plone.core.services.plone_service import PloneService, PloneServiceContainer, IFormatQueryResults


class ATFolderService(PloneServiceContainer):
    adapts(IBaseFolder)
    # implements(IService)


class ATObjectService(PloneService):
    adapts(IBaseObject)
    # implements(IService)


class ATTopicService(PloneServiceContainer):
    """ATTopic is special. Therefore it needs its own service adapter."""
    adapts(IATTopic)
    # implements(IServiceContainer)

    def get_misc(self, as_callback=False):
        misc = PloneServiceContainer.get_misc(self, as_callback)
        if as_callback:
            query_args = self.context.buildQuery()
            misc['contents.callback'] = {'function': 'query', 'args': (query_args,)}
        else:
            brains = self.context.queryCatalog()
            formatter = getUtility(IFormatQueryResults)
            collection = formatter(brains)
            if collection:
                misc['contents'] = collection

        formatted_criteria = {}
        for criterion in self.context.listCriteria():
            criterion_id = criterion.getId()
            formatted_criteria[criterion_id] = {}
            # criterion.schema apparently does not have a keys()
            fields = dict(zip(criterion.schema.keys(), criterion.schema.values()))
            for field in fields:
                f = fields[field]
                formatted_criteria[criterion_id][f.getName()] = {
                    'type': f.type,
                    'required': f.required,
                    'value': criterion[field]}
        misc['criteria'] = formatted_criteria
        return misc
