import unittest

class DeliveranceSelectTests(unittest.TestCase):

    _started = None

    def _getTargetClass(self):
        from repoze.dvselect import DeliveranceSelect
        return DeliveranceSelect

    def _makeOne(self, application):
        return self._getTargetClass()(application)

    def _startResponse(self, status, headers, exc_info=None):
        self._started = (status, headers, exc_info)

    def _makeApplication(self):
        def _app(environ, start_response):
            start_response('200 OK', ())
            return ['body']
        return _app

    def test_ctor_no_filename(self):
        application = self._makeApplication()
        mw = self._makeOne(application)
        self.failUnless(mw.application is application)

    def test___call___w_no_assertions(self):
        application = self._makeApplication()
        mw = self._makeOne(application)
        environ = {}

        result = mw(environ, self._startResponse)

        self.assertEqual(self._started, ('200 OK', (), None))
        self.assertEqual(environ.get('deliverance.theme_uri'), None)
        self.assertEqual(environ.get('deliverance.rule_uri'), None)

    def test___call___w_theme_assertion(self):
        application = self._makeApplication()
        mw = self._makeOne(application)
        environ = {'repoze.urispace.assertions':
                    {'theme': 'http://dv.example.com/theme.html'}}

        result = mw(environ, self._startResponse)

        self.assertEqual(self._started, ('200 OK', (), None))
        self.assertEqual(environ.get('deliverance.theme_uri'), 
                                     'http://dv.example.com/theme.html')
        self.assertEqual(environ.get('deliverance.rule_uri'), None)

    def test___call___w_rules_assertion(self):
        application = self._makeApplication()
        mw = self._makeOne(application)
        environ = {'repoze.urispace.assertions':
                    {'rules': 'http://dv.example.com/rules.xml'}}

        result = mw(environ, self._startResponse)

        self.assertEqual(self._started, ('200 OK', (), None))
        self.assertEqual(environ.get('deliverance.theme_uri'), None)
        self.assertEqual(environ.get('deliverance.rule_uri'), 
                                     'http://dv.example.com/rules.xml')

    def test___call___w_theme_and_rules_assertions(self):
        application = self._makeApplication()
        mw = self._makeOne(application)
        environ = {'repoze.urispace.assertions':
                    {'theme': 'http://dv.example.com/theme.html',
                     'rules': 'http://dv.example.com/rules.xml',
                    }
                  }

        result = mw(environ, self._startResponse)

        self.assertEqual(self._started, ('200 OK', (), None))
        self.assertEqual(environ.get('deliverance.theme_uri'), 
                                     'http://dv.example.com/theme.html')
        self.assertEqual(environ.get('deliverance.rule_uri'), 
                                     'http://dv.example.com/rules.xml')
