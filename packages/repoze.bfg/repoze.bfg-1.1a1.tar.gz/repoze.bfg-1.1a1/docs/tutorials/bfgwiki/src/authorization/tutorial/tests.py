import unittest

from repoze.bfg import testing

class PageModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from tutorial.models import Page
        return Page

    def _makeOne(self, data=u'some data'):
        return self._getTargetClass()(data=data)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.data, u'some data')
        
class WikiModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from tutorial.models import Wiki
        return Wiki

    def _makeOne(self):
        return self._getTargetClass()()

    def test_it(self):
        wiki = self._makeOne()
        self.assertEqual(wiki.__parent__, None)
        self.assertEqual(wiki.__name__, None)

class AppmakerTests(unittest.TestCase):
    def _callFUT(self, zodb_root):
        from tutorial.models import appmaker
        return appmaker(zodb_root)

    def test_it(self):
        root = {}
        self._callFUT(root)
        self.assertEqual(root['app_root']['FrontPage'].data,
                         'This is the front page')

class ViewWikiTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        
    def tearDown(self):
        testing.cleanUp()

    def test_it(self):
        from tutorial.views import view_wiki
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = view_wiki(context, request)
        self.assertEqual(response.location, 'http://example.com/FrontPage')

class ViewPageTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        
    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from tutorial.views import view_page
        return view_page(context, request)

    def test_it(self):
        wiki = testing.DummyModel()
        wiki['IDoExist'] = testing.DummyModel()
        context = testing.DummyModel(data='Hello CruelWorld IDoExist')
        context.__parent__ = wiki
        context.__name__ = 'thepage'
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/view.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.request, request)
        self.assertEqual(
            renderer.content,
            '<div class="document">\n'
            '<p>Hello <a href="http://example.com/add_page/CruelWorld">'
            'CruelWorld</a> '
            '<a href="http://example.com/IDoExist/">'
            'IDoExist</a>'
            '</p>\n</div>\n')
        self.assertEqual(renderer.edit_url,
                         'http://example.com/thepage/edit_page')
        
    
class AddPageTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        
    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from tutorial.views import add_page
        return add_page(context, request)

    def test_it_notsubmitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.subpath = ['AnotherPage']
        renderer = testing.registerDummyRenderer('templates/edit.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.request, request)
        self.assertEqual(renderer.page.data, '')
        
    def test_it_submitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        request.subpath = ['AnotherPage']
        response = self._callFUT(context, request)
        page = context['AnotherPage']
        self.assertEqual(page.data, 'Hello yo!')
        self.assertEqual(page.__name__, 'AnotherPage')
        self.assertEqual(page.__parent__, context)

class EditPageTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        
    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from tutorial.views import edit_page
        return edit_page(context, request)

    def test_it_notsubmitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/edit.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.request, request)
        self.assertEqual(renderer.page, context)
        
    def test_it_submitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        renderer = testing.registerDummyRenderer('templates/edit.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')
        self.assertEqual(context.data, 'Hello yo!')
        
        
        
