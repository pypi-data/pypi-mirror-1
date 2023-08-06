from zope.interface import Interface, Attribute


class IScrubber(Interface):
    """This utility is intended to scrub a data structure clean so that an can be
    marshalled for whatever web service is requesting the data structure.
    """

    def dict_scrub(data):
        """This method will clean a dictionary and bring any of its data types to
        the standard built-in types or types that are known to marshall.
        """


class IService(Interface):
    """Adapts an object to an XML-RPC compatible format."""

    def get_skeleton(filtr=[]):
        """Get a skeleton data structure of the object without its values."""

    def get_object(attrs=[]):
        """Represent the object in serviceable output. See this package's
        specification for further information on servicible output.
        """

    def get_type():
        """A type name representative of the type across the plone system. More
        importantly it should be the name proper name and not the user friendly name.
        """

    def get_misc(as_callback=False):
        """Get any miscellaneous data associated with the object (contents,
        computed results, etc.)
        """

    def set_properties(params):
        """Given a dictionary of parameters, set_properities attempts to set the
        context's attributes with the data.
        """

    def clipboard(action, target, destination):
        """Clipboard actions... copy, cut and paste. paste is implied from
        either copy or cut action."""


class IServiceContainer(IService):

    def create_object(type_name, id_):
        """Create a child object of the parent object given the type_name and name it with id_
        """

    def delete_object(id_):
        """Delete the child object from the id_ given. Returns True if the process
        was successful."""


class IContextBuilder(Interface):
    """Builds the context from a given context (most likely the site) and string path."""


class IServiceLookup(Interface):
    """Finds an object from a context and string path and provides the Serviced
    object as its result."""


class IFormatQueryResults(Interface):
    """Given a list of brains, this utility will provide spec formatted output for a
    portal_catalog query."""