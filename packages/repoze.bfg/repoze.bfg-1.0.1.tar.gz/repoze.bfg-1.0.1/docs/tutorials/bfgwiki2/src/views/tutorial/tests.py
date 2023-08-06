import unittest
from repoze.bfg import testing

def _initTestingDB():
    from tutorial.models import initialize_sql
    session = initialize_sql('sqlite://')
    return session

class TestMyView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        _initTestingDB()
        
    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from tutorial.views import my_view
        return my_view(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/mytemplate.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.root.name, 'root')
        self.assertEqual(renderer.request, request)
        self.assertEqual(renderer.project, 'tutorial')
