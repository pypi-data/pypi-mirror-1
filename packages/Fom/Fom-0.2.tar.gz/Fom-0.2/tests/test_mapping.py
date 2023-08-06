import uuid
import unittest

from fom.db import PRIMITIVE_CONTENT_TYPE
from fom.dev import sandbox_fluid
from fom.mapping import (path_split, path_child, Namespace, Tag, Object,
    tag_relation, tag_value)
from fom.errors import Fluid404Error, Fluid412Error



class TestPath(unittest.TestCase):

    def test_parent(self):
        self.assertEquals(path_split(u'goo/moo'), [u'goo', u'moo'])

    def test_child(self):
        self.assertEquals(path_child(u'foo', u'blah'), u'foo/blah')

    def test_empty(self):
        self.assertEquals(path_child(u'', 'foo'), u'foo')


class NamespaceTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()
        self.uid = str(uuid.uuid4())
        self.path = u'test/%s' % self.uid

    def test_new(self):
        n = Namespace(u'test')
        self.assertEquals(n.path, u'test')
        self.assertTrue(n.fluid is self.fluid)

    def test_create(self):
        ns = Namespace(self.path)

        ns.create(u'fomtest description')

        childns = ns.create_namespace(u'child', u'fomtest child')
        childns.delete()

        # access the namespace's low-level api
        ns.api.get()
        ns.api.put(u'A better description')
        ns.api.post(u'child', u'fomtest child')

        childNs = Namespace(u'%s/%s' % (self.path, u'child'))
        childNs.delete()

        ns.delete()

    def test_description(self):
        ns = Namespace(self.path)
        ns.create(u'testdesc')
        self.assertEquals(ns.description, u'testdesc')
        ns.description = u'newdesc'
        self.assertEquals(ns.description, u'newdesc')

    def test_create_child(self):
        n = Namespace(u'test')
        child = n.create_namespace(self.uid, u'fomtest description')
        self.assertEquals(child.path, self.path)
        child.delete()

    def test_child_namespace(self):
        n = Namespace(u'test')
        child = n.namespace(u'test')
        self.assertTrue(isinstance(child, Namespace))
        self.assertEquals(child.path, u'test/test')

    def test_child_tag(self):
        n = Namespace(u'test')
        child = n.tag(u'test')
        self.assertTrue(isinstance(child, Tag))
        self.assertEquals(child.path, u'test/test')


class ObjectTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

    def testNew(self):
        o = Object()
        self.assertTrue(o.path is None)
        self.assertTrue(o.uid is None)

    def testCreate(self):
        o = Object()
        o.create()
        self.assert_(o.uid)

    def testGet(self):
        o = Object()
        o.create()
        self.assertRaises(Fluid404Error, o.get, 'test/fomtest')

    def testSetPrimitive(self):
        o = Object()
        o.create()
        self.assertRaises(Fluid404Error, o.get, 'test/fomtest')
        for value in (None, True, False, 123, 45.67, 'hey there'):
            o.set('test/fomtest', value)
            self.assertEqual(o.get('test/fomtest'),
                (value, PRIMITIVE_CONTENT_TYPE))

    def testSetOpaque(self):
        o = Object()
        o.create()
        self.assertRaises(Fluid404Error, o.get, 'test/fomtest')
        o.set('test/fomtest', 'xyz', 'application/bananas')
        self.assertEqual(o.get('test/fomtest'), ('xyz', 'application/bananas'))

    def testHas(self):
        o = Object()
        o.create()
        self.assertFalse(o.has('test/fomtest'))
        o.set('test/fomtest', 123)
        self.assertTrue(o.has('test/fomtest'))

    def testTags(self):
        o = Object()
        o.create()
        self.assertEquals(o.tag_paths, [])
        self.assertEquals(o.tags, [])
        o.set('test/fomtest', 123)
        self.assertTrue('test/fomtest' in o.tag_paths)
        self.assertEquals(o.tags[0].path, 'test/fomtest')


class TagTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

    def testNew(self):
        t = Tag('test/fomtest')
        self.assertEquals(t.path, 'test/fomtest')

    def testGetDescription(self):
        t = Tag('test/fomtest')
        t.description = u'banana'
        self.assertEquals(t.description, u'banana')

    def testSetDescription(self):
        t = Tag('test/fomtest')
        t.description = u'melon'
        self.assertEquals(t.description, u'melon')


class RelationTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

        n = Namespace(u'test')
        for name in (u'fomtest', u'fomtest2'):
            try:
                n.create_tag(u'fomtest', u'%s description' % name, False)
            except Fluid412Error:
                pass
        
        class A(Object):
            fomtest = tag_relation(u'test/fomtest')
            fomtest2 = tag_value(u'test/fomtest2')

        self.A = A

    def testRelation(self):
        a1 = self.A()
        a1.create()

        a2 = self.A()
        a2.create()

        a1.fomtest = a2

        self.assertEqual(a1.fomtest.uid, a2.uid)

    def testMissingValue(self):
        a1 = self.A()
        a1.create()
        try:
            a1.fomtest2
        except Fluid404Error:
            pass
        else:
            self.fail('Failed to raise Fluid404Error')

    def testValue(self):
        a1 = self.A()
        a1.create()
        a1.fomtest2 = 'hello'
        self.assertEquals(a1.fomtest2, 'hello')


if __name__ == '__main__':
    unittest.main()
