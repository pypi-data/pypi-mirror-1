import unittest

from repoze.bfg.testing import cleanUp
from repoze.bfg import testing

class TestRendererFromCache(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, factory, level=3, **kw):
        from repoze.bfg.templating import renderer_from_cache
        return renderer_from_cache(path, factory, level, **kw)

    def test_abspath_notfound(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        abspath = '/wont/exist'
        testing.registerUtility({}, ITemplateRenderer, name=abspath)
        self.assertRaises(ValueError, self._callFUT, abspath, None)

    def test_abspath_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=abspath)
        result = self._callFUT(abspath, None)
        self.failUnless(result is renderer)

    def test_abspath_notyetregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=abspath)
        result = self._callFUT(abspath, None)
        self.failUnless(result is renderer)

    def test_relpath_path_registered(self):
        renderer = {}
        from repoze.bfg.interfaces import ITemplateRenderer
        testing.registerUtility(renderer, ITemplateRenderer, name='foo/bar')
        result = self._callFUT('foo/bar', None)
        self.failUnless(renderer is result)

    def test_relpath_is_package_registered(self):
        renderer = {}
        from repoze.bfg.interfaces import ITemplateRenderer
        testing.registerUtility(renderer, ITemplateRenderer, name='foo:bar/baz')
        result = self._callFUT('foo:bar/baz', None)
        self.failUnless(renderer is result)

    def test_relpath_notfound(self):
        self.assertRaises(ValueError, self._callFUT, 'wont/exist', None)

    def test_relpath_is_package_notfound(self):
        from repoze.bfg import tests
        module_name = tests.__name__
        self.assertRaises(ValueError, self._callFUT,
                          '%s:wont/exist' % module_name, None)

    def test_relpath_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_templating.py'
        spec = '%s:%s' % (module_name, relpath)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=spec)
        result = self._callFUT('test_templating.py', None)
        self.failUnless(result is renderer)

    def test_relpath_is_package_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_templating.py'
        spec = '%s:%s' % (module_name, relpath)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=spec)
        result = self._callFUT(spec, None)
        self.failUnless(result is renderer)

    def test_relpath_notyetregistered(self):
        import os
        from repoze.bfg.tests import test_templating
        module_name = test_templating.__name__
        relpath = 'test_templating.py'
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('test_templating.py', factory)
        self.failUnless(result is renderer)
        path = os.path.abspath(__file__)
        if path.endswith('pyc'): # pragma: no cover
            path = path[:-1]
        self.assertEqual(factory.path, path)
        self.assertEqual(factory.kw, {})

    def test_relpath_is_package_notyetregistered(self):
        import os
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_templating.py'
        renderer = {}
        factory = DummyFactory(renderer)
        spec = '%s:%s' % (module_name, relpath)
        result = self._callFUT(spec, factory)
        self.failUnless(result is renderer)
        path = os.path.abspath(__file__)
        if path.endswith('pyc'): # pragma: no cover
            path = path[:-1]
        self.assertEqual(factory.path, path)
        self.assertEqual(factory.kw, {})

    def test_reload_resources_true(self):
        from zope.component import queryUtility
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ITemplateRenderer
        settings = {'reload_resources':True}
        testing.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('test_templating.py', factory)
        self.failUnless(result is renderer)
        spec = '%s:%s' % ('repoze.bfg.tests', 'test_templating.py')
        self.assertEqual(queryUtility(ITemplateRenderer, name=spec),
                         None)

    def test_reload_resources_false(self):
        from zope.component import queryUtility
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ITemplateRenderer
        settings = {'reload_resources':False}
        testing.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('test_templating.py', factory)
        self.failUnless(result is renderer)
        spec = '%s:%s' % ('repoze.bfg.tests', 'test_templating.py')
        self.assertNotEqual(queryUtility(ITemplateRenderer, name=spec),
                            None)

class DummyFactory:
    def __init__(self, renderer):
        self.renderer = renderer

    def __call__(self, path, **kw):
        self.path = path
        self.kw = kw
        return self.renderer
    

