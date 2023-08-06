import random

from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.interface import implements

from wsapi4plone.core.browser.interfaces import IApplicationAPI
from wsapi4plone.core.browser.wsapi import WSAPI
from wsapi4plone.core.interfaces import IScrubber, IService, IServiceContainer


class ApplicationAPI(WSAPI):
    implements(IApplicationAPI)

    def get_object(self, paths=['',]):
        """
        @param paths - list of strings to the path of the wanted objects
                     - [path, ...]
        =returns { path: [{ attr: value, ...}, type_name, {misc}], ...}
        """
        objs = {}
        for path in paths:
            obj = self.builder(self.context, path)
            serviced_obj = IService(obj)
            data = serviced_obj.get_object()
            type_ = serviced_obj.get_type()
            misc = serviced_obj.get_misc()
            objs[path] = (data, type_, misc,)
            self.logger.info("- get_object - Gathering data for %s." % obj)
        return objs

    def post_object(self, params):
        """
        @param params - dictionary of path with a list value where list item zero are
                        attribute names and their respective values; and list item one
                        is the type name.
                      - { path: [{ attr: value, ...}, type_name], ...}
        =returns [path, ...]
        """
        assert type(params) == dict, "The first agument must be a dictionary."

        results = []
        for path in params:
            properties, type_name = params[path][0:2]
            # start by getting the parent object
            obj = self.builder(self.context, path)
            serviced_obj = IServiceContainer(obj)

            # create the child object
            id_ = properties.get('id', None)
            assert id_ is not None, "An 'id' must be provided in the list of attributes"
            assert type_name is not None, "A type must be given."
            created_obj_id = serviced_obj.create_object(type_name, id_)
            self.logger.info("- post_object - Creating object at %s of %s type." % (obj, type_name))
            results.append(created_obj_id)

            # set the additional values
            created_obj = self.builder(obj, created_obj_id)
            serviced_created_obj = IService(created_obj)
            serviced_created_obj.set_properties(properties)
            self.logger.info("- post_object - Set properties for %s." % created_obj)
        return results

    def put_object(self, params):
        """
        @param params - dictionary of path with a list value where list item zero are
                        attribute names and their respective values; and list item one
                        is the type name.
                      - { path: [{ attr: value, ...}], ...}
        =returns [path, ...]
        """
        assert type(params) == dict, "The first argument must be a dictionary."

        results = []
        for path in params:
            properties = params[path][0]
            obj = self.builder(self.context, path)
            serviced_obj = IService(obj)
            self.logger.info("- put_object - Set properties for %s." % obj)
            serviced_obj.set_properties(properties)
            results.append(obj.id)
            # TODO pumazi: notifiers and possibly reindex
        return results

    def delete_object(self, paths=['',]):
        """
        @param paths - list of strings to the path of the wanted objects
                     - [path, ...]
        =returns None
        """
        for path in paths:
            path = path.strip('/')
            delete_path = path
            path = path.split('/')
            delete_id = u''.join(path[-1:])
            path = u'/'.join(path[:-1])

            obj = self.builder(self.context, path)
            parent_serviced_obj = IServiceContainer(obj)
            self.logger.info("- delete_object - Deleting %s from %s." % (delete_id, obj))
            parent_serviced_obj.delete_object(delete_id)
        return

    def get_schema(self, type_name, path=''):
        """
        @param type_name - the formal system name of the content-type
        @param path - string to the path of the container
                    - sometimes necessary if content-type contraints are defined
        =returns { attr: {required: True | False, type: type_string, ...}, ...}
        """
        # TODO pumazi: may want to eventually cache the schema types so that
        # objects don't need created on every types enabled call
        context = self.builder(self.context, path)
        uid = 'tmp_'+path+'_'+str(random.randint(1, 1000000))
        path = context.invokeFactory(type_name=type_name, id=uid)
        self.logger.info("- get_schema - Getting schema for %s type with temporary name %s on %s." % (type_name, uid, context))
        obj = self.builder(self.context, path)
        serviced_obj = IService(obj)
        skeleton = serviced_obj.get_skeleton()
        context.manage_delObjects(uid)
        return skeleton
