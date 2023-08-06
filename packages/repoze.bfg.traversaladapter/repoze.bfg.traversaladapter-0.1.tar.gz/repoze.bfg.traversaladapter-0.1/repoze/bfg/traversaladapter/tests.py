import unittest
from zope.interface import implements
from zope.interface import Interface
from zope.interface import Attribute
from zope.testing.cleanup import cleanUp

from repoze.bfg.traversaladapter import ITraversalAdapterFactory

class TraversalProxyTestBase(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.traversaladapter import ModelGraphTraverser
        return ModelGraphTraverser

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def _getEnviron(self, **kw):
        environ = {}
        environ.update(kw)
        return environ

class ModelGraphTraverserTests(TraversalProxyTestBase):

    def test_class_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITraverser
        verifyClass(ITraverser, self._getTargetClass())

    def test_instance_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITraverser
        context = DummyContext()
        verifyObject(ITraverser, self._makeOne(context))

    def test_call_with_no_pathinfo(self):
        policy = self._makeOne(None)
        environ = self._getEnviron()
        result = policy(environ)
        self.assertEqual(result['context'], None)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], policy.root)
        self.assertEqual(result['virtual_root'], policy.root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_pathel_with_no_getitem(self):
        policy = self._makeOne(None)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        result = policy(environ)
        self.assertEqual(result['context'], None)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ('bar',))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], policy.root)
        self.assertEqual(result['virtual_root'], policy.root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        root = DummyContext()
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='')
        result = policy(environ)
        self.assertEqual(result['context'], root)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_withpath_nosubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        result = policy(environ)
        self.assertEqual(result['context'], foo)
        self.assertEqual(result['view_name'], 'bar')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo',))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_withpath_withsubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz/buz')
        result = policy(environ)
        self.assertEqual(result['context'], foo)
        self.assertEqual(result['view_name'], 'bar')
        self.assertEqual(result['subpath'], ('baz', 'buz'))
        self.assertEqual(result['traversed'], (u'foo',))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_explicit_viewname(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/@@foo')
        result = policy(environ)
        self.assertEqual(result['context'], root)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_vh_root(self):
        environ = self._getEnviron(PATH_INFO='/baz',
                                   HTTP_X_VHM_ROOT='/foo/bar')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        result = policy(environ)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], bar)
        self.assertEqual(result['virtual_root_path'], (u'foo', u'bar'))

    def test_call_with_vh_root2(self):
        environ = self._getEnviron(PATH_INFO='/bar/baz',
                                   HTTP_X_VHM_ROOT='/foo')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        result = policy(environ)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], foo)
        self.assertEqual(result['virtual_root_path'], (u'foo',))

    def test_call_with_vh_root3(self):
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz',
                                   HTTP_X_VHM_ROOT='/')
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        policy = self._makeOne(root)
        result = policy(environ)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_vh_root4(self):
        environ = self._getEnviron(PATH_INFO='/',
                                   HTTP_X_VHM_ROOT='/foo/bar/baz')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        result = policy(environ)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], baz)
        self.assertEqual(result['virtual_root_path'], (u'foo', u'bar', u'baz'))

    def test_non_utf8_path_segment_unicode_path_segments_fails(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        segment = unicode('LaPe\xc3\xb1a', 'utf-8').encode('utf-16')
        environ = self._getEnviron(PATH_INFO='/%s' % segment)
        self.assertRaises(TypeError, policy, environ)

    def test_non_utf8_path_segment_settings_unicode_path_segments_fails(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        segment = unicode('LaPe\xc3\xb1a', 'utf-8').encode('utf-16')
        environ = self._getEnviron(PATH_INFO='/%s' % segment)
        self.assertRaises(TypeError, policy, environ)

    def test_withroute_nothingfancy(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        routing_args = ((), {})
        environ = {'bfg.routes.matchdict': {}}
        result = traverser(environ)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_withroute_with_subpath(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = {'bfg.routes.matchdict': {'subpath':'/a/b/c'}}
        result = traverser(environ)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ('a', 'b','c'))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_withroute_and_traverse(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = {'bfg.routes.matchdict': {'traverse':'foo/bar'}}
        result = traverser(environ)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ('bar',))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

class TraversalAdapterTests(TraversalProxyTestBase):

    def setUp(self):
        TraversalProxyTestBase.setUp(self)

    def tearDown(self):
        from zope.component import getSiteManager
        getSiteManager.reset()
        TraversalProxyTestBase.tearDown(self)

    def test_register_class(self):
        self._register_traversal_adapter(NamedItemCollection, LocationAdapter)
        root, parent, child = self._make_graph()
        traverser = self._makeOne(root)
        match = traverser(dict(PATH_INFO='/parent/children'))
        ctx = match['context']
        self.assertTrue(isinstance(ctx, LocationAdapter))
        self.assertTrue(ctx.__parent__ is parent)
        self.assertEqual(ctx.__name__, 'children')

    def test_register_interface(self):
        self._register_traversal_adapter(INamedChild, LocationAdapter)
        root, parent, child = self._make_graph()
        traverser = self._makeOne(root)
        match = traverser(dict(PATH_INFO='/parent/children/foo'))
        ctx = match['context']
        self.assertTrue(isinstance(ctx, LocationAdapter))
        self.assertEqual(ctx.name, 'foo')
        self.assertTrue(ctx.__parent__ is parent.children)
        self.assertEqual(ctx.__name__, 'foo')

    def test_register_root(self):
        self._register_traversal_adapter(Root, LocationAdapter)
        root, parent, child = self._make_graph()
        traverser = self._makeOne(root)
        match = traverser(dict(PATH_INFO='/'))
        ctx = match['context']
        self.assertTrue(isinstance(ctx, LocationAdapter))
        self.assertEqual(ctx.__name__, 'root')

    def test_register_factory_for_class(self):
        self._register_traversal_adapter(NamedItemCollection,
                                         location_adapter_factory)
        root, parent, child = self._make_graph()
        traverser = self._makeOne(root)
        match = traverser(dict(PATH_INFO='/parent/children'))
        ctx = match['context']
        self.assertTrue(isinstance(ctx, LocationAdapter))
        self.assertTrue(ctx.__parent__ is parent)
        self.assertEqual(ctx.__name__, 'children')

    def _register_traversal_adapter(self, type_or_iface, adapter_class):
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerAdapter(adapter_class, (type_or_iface,),
                           ITraversalAdapterFactory)

    def _make_graph(self):
        root = Root()
        parent = Parent()
        root['parent'] = parent
        child = Child('foo')
        parent.children.append(child)
        return root, parent, child

class LocationAdapter(object):
    def __init__(self, obj, parent, name):
        self.__obj = obj
        self.__parent__ = parent
        self.__name__ = name

    def __getattr__(self, attr):
        return getattr(self.__obj, attr)

def location_adapter_factory(obj, parent, name):
    return LocationAdapter(obj, parent, name)

class Root(dict):
    pass

class INamedChild(Interface):
    name = Attribute('Child name.')

class Child(object):
    implements(INamedChild)
    def __init__(self, name):
        self.name = name

class NamedItemCollection(list):
    def __init__(self):
        super(NamedItemCollection, self).__init__()
        self.__name_map = {}
    def append(self, item):
        super(NamedItemCollection, self).append(item)
        self.__name_map[item.name] = item
    def __getitem__(self, name):
        return self.__name_map[name]

class IParent(Interface):
    children = Attribute("Collection of children.")

class Parent(object):
    implements(IParent)
    def __init__(self):
        self.children = NamedItemCollection()
    def __getitem__(self, item):
        return getattr(self, item)

class DummyContext(object):
    __parent__ = None
    def __init__(self, next=None, name=None):
        self.next = next
        self.__name__ = name

    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next

    def __repr__(self): #pragma: no cover
        return '<DummyContext with name %s at id %s>'%(self.__name__, id(self))

