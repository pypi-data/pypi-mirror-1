from zope.app.container.interfaces import IContainer
from zope.component import adapts
from zope.interface import implements, implementsOnly, Interface

from wsapi4plone.core.interfaces import IService, IServiceContainer

class Service(object):
    """The service base class."""
    adapts(Interface)
    implements(IService)

    def __init__(self, context):
        self.context = context

    def get_skeleton(self, filtr=[]):
        raise NotImplementedError(
            "%s does not implement the get_skeleton method. Attempting to adapt %s." % (self.__class__.__name__, self.context))

    def get_object(self, attrs=[]):
        raise NotImplementedError(
            "%s does not implement the get_object method. Attempting to adapt %s." % (self.__class__.__name__, self.context))

    def get_type(self):
        raise NotImplementedError(
            "%s does not implement the get_type method. Attempting to adapt %s." % (self.__class__.__name__, self.context))

    def get_misc(self, as_callback=False):
        raise NotImplementedError(
            "%s does not implement the get_misc method. Attempting to adapt %s." % (self.__class__.__name__, self.context))

    def set_properties(self, params):
        raise NotImplementedError(
            "%s does not implement the set_properties method. Attempting to adapt %s." % (self.__class__.__name__, self.context))

    def clipboard(self, action, target, destination):
        raise NotImplementedError(
            "%s does not implement the clipboard method. Attempting to adapt %s." % (self.__class__.__name__, self.context))


class ServiceContainer(Service):
    adapts(IContainer)
    implementsOnly(IServiceContainer)

    def delete_object(self, id_):
        raise NotImplementedError(
            "%s does not implement the delete_object method. Attempting to adapt %s." % (self.__class__.__name__, self.context))

    def create_object(self, type_name, id_):
        raise NotImplementedError(
            "%s does not implement the create_object method. Attempting to adapt %s." % (self.__class__.__name__, self.context))
