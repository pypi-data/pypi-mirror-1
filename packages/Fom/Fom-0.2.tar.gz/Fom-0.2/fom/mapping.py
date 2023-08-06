# -*- coding: utf-8 -*-

"""
    fom.mapping
    ~~~~~~~~~~~

    Object orientated interface into FluidDB

    :copyright: 2010 Fom Authors.
    :license: MIT, see LICENSE for more information.
"""


from fom.session import Fluid
from fom.errors import Fluid404Error


class SessionBound(object):
    """Something with a path that is bound to a database.

    .. attribute:: path

        The path of the item relative to the toplevel.

    .. attribute:: fluid

        The instance of fom.session.Fluid bound to this item.
    """

    def __init__(self, path, fluid=None):
        self.path = path
        if fluid is None:
            fluid = Fluid.bound
        self.fluid = fluid


class Namespace(SessionBound):
    """A Namespace
    """

    @property
    def api(self):
        return self.fluid.namespaces[self.path]

    def delete(self):
        """Delete this namespace
        """
        return self.api.delete()

    def create(self, description):
        """Create this namespace.

        :param description: The description of the Namespace
        """
        parent, name = path_split(self.path)
        parent_api = self.fluid.namespaces[parent]
        return parent_api.post(name, description)

    def create_namespace(self, name, description):
        """Create a child namespace, and return it.

        :param name: The name of the Namespace to be created
        :param description: The description of the Namespace to be created
        """
        self.api.post(name, description)
        return Namespace(path_child(self.path, name))

    def create_tag(self, name, description, indexed):
        """Create a tag in this namespace.
        """
        return self.fluid.tags[self.path].post(name, description, indexed)

    def _get_description(self):
        """Get the description for a tag.
        """
        r = self.api.get(returnDescription=True)
        return r.value[u'description']

    def _set_description(self, description):
        """Set the description for a tag.
        """
        return self.api.put(description)

    description = property(_get_description, _set_description)

    @property
    def tag_names(self):
        """Return the tag names.
        """
        r = self.api.get(returnTags=True)
        return r.value[u'tagNames']

    @property
    def tag_paths(self):
        """Return the tag paths
        """
        return [
            path_child(self.path, child) for child in self.tag_names
        ]

    @property
    def tags(self):
        return [
            Tag(path) for path in self.tag_paths
        ]

    @property
    def namespace_names(self):
        """Return the namespace names.
        """
        r = self.api.get(returnNamespaces=True)
        return r.value[u'namespaceNames']

    @property
    def namespace_paths(self):
        """Return the namespace paths.
        """
        return [
            path_child(self.path, child) for child in self.namespace_names
        ]

    @property
    def namespaces(self):
        """Return the child namespaces.
        """
        return [
            Namespace(path) for path in self.namespace_paths
        ]

    def tag(self, name):
        """Get a child tag.
        """
        return Tag(path_child(self.path, name))

    def namespace(self, name):
        """Get a child namespace.
        """
        return Namespace(path_child(self.path, name))


class Tag(SessionBound):
    """A Tag
    """

    @property
    def api(self):
        """The api TagApi for this instance.
        """
        return self.fluid.tags[self.path]

    def _get_description(self):
        """Get the description for a tag.
        """
        r = self.api.get(returnDescription=True)
        return r.value[u'description']

    def _set_description(self, description):
        """Set the description for a tag.
        """
        return self.api.put(description)

    description = property(_get_description, _set_description)


class Object(SessionBound):
    """An object
    """

    def __init__(self, uid=None, fluid=None):
        SessionBound.__init__(self, uid, fluid)

    def create(self, about=None):
        """Create a new object.
        """
        r = self.fluid.objects.post(about)
        self.path = r.value[u'id']

    @property
    def uid(self):
        return self.path

    @property
    def api(self):
        """The api ObjectApi for this instance.
        """
        return self.fluid.objects[self.path]

    def get(self, tag):
        """Get the value of a tag.
        """
        tagpath = tag
        r = self.api[tagpath].get()
        return r.value, r.content_type

    def set(self, tag, value, valueType=None):
        """Set the value of a tag.
        """
        tagpath = tag
        self.api[tagpath].put(value, valueType)

    def has(self, tag):
        """Check if an object has a tag.
        """
        tagpath = tag
        try:
            self.api[tagpath].head()
        except Fluid404Error:
            return False
        else:
            return True

    @property
    def tag_paths(self):
        r = self.api.get()
        return r.value[u'tagPaths']

    @property
    def tags(self):
        return [Tag(path) for path in self.tag_paths]


class tag_value(object):
    """Descriptor to provide a tag value lookup on an object to simulate a
    simple attribute.
    """

    def __init__(self, tag):
        self.tagpath = tag

    def __get__(self, instance, owner):
        return instance.get(self.tagpath)[0]

    def __set__(self, instance, value, valueType=None):
        return instance.set(self.tagpath, value, valueType)


class tag_relation(tag_value):
    """Descriptor to provide a relation lookup.

    An id is actually stored in the database.
    """

    def __init__(self, tag, object_type=Object):
        tag_value.__init__(self, tag)
        self.object_type = object_type

    def __get__(self, instance, owner):
        uid = tag_value.__get__(self, instance, owner)
        return self.object_type(uid)

    def __set__(self, instance, value):
        return tag_value.__set__(self, instance, value.uid)


def path_child(path, child):
    """Get the named child for a path.
    """
    if path == '':
        return child
    else:
        return '/'.join((path, child))


def path_split(path):
    """Split a path into parent, self
    """
    return path.rsplit('/', 1)
