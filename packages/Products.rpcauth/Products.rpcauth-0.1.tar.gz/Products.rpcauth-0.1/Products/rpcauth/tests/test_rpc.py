import unittest

class BinarifyTests(unittest.TestCase):

    def _callFUT(self, mapping):
        from Products.rpcauth.rpc import binarify
        return binarify(mapping)

    def test_empty(self):
        self.assertEqual(self._callFUT({}), {})

    def test_string(self):
        import xmlrpclib
        self.assertEqual(self._callFUT({'foo': 'foo'}),
                         {'foo': xmlrpclib.Binary('foo')})

    def test_unicode(self):
        import xmlrpclib
        self.assertEqual(self._callFUT({'bar': u'bar'}),
                         {'bar': xmlrpclib.Binary(u'bar')})

    def test_non_strings(self):
        splif = object()
        self.assertEqual(self._callFUT({'baz': 1,
                                        'qux': 0.3,
                                        'splif': splif,
                                       }),
                         {'baz': 1,
                          'qux': 0.3,
                          'splif': splif
                         })

class DebinarifyTests(unittest.TestCase):

    def _callFUT(self, mapping):
        from Products.rpcauth.rpc import debinarify
        return debinarify(mapping)

    def test_empty(self):
        self.assertEqual(self._callFUT({}), {})

    def test_string(self):
        import xmlrpclib
        self.assertEqual(self._callFUT({'foo': xmlrpclib.Binary('foo')}),
                         {'foo': 'foo'})

    def test_unicode(self):
        import xmlrpclib
        self.assertEqual(self._callFUT({'bar': xmlrpclib.Binary(u'bar')}),
                         {'bar': u'bar'})

    def test_non_strings(self):
        splif = object()
        self.assertEqual(self._callFUT({'baz': 1,
                                        'qux': 0.3,
                                        'splif': splif,
                                       }),
                         {'baz': 1,
                          'qux': 0.3,
                          'splif': splif
                         })

class CheckCredentialsViewTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.rpcauth.rpc import CheckCredentialsView
        return CheckCredentialsView

    def _makeContext(self, parent=None):
        from Acquisition import Implicit
        class DummyContext(Implicit):
            pass
        result = DummyContext()
        if parent is not None:
            result = result.__of__(parent)
        return result

    def _makeOne(self, context=None, request=None):
        if context is None:
            context = self._makeContext()
        if request is None:
            request = {}
        return self._getTargetClass()(context, request)

    def _makePAS(self, userid, login, password):
        from Products.PluggableAuthService.interfaces.plugins import \
            IAuthenticationPlugin
        class DummyAuthenticator:
            def authenticateCredentials(self, credentials):
                if (credentials['login'] == login and
                    credentials['password'] == password):
                    return (userid, login)
        class DummyPlugins:
            def listPlugins(self, iface):
                if iface is IAuthenticationPlugin:
                    return [('dummy', DummyAuthenticator())]
                return ()
        _marker = object()
        class DummyPAS:
            plugins = DummyPlugins()
            def _getOb(self, id, default=_marker):
                if id == 'plugins':
                    return self.plugins
                if default is _marker:
                    raise AttributeError(id)
                return default
        return DummyPAS()

    def test___call___no_pas(self):
        view = self._makeOne()
        self.assertEqual(view({}), {})

    def test___call___direct_pas_hit(self):
        view = self._makeOne()
        view.context.acl_users = self._makePAS('phred',
                                                'phred@example.com', 'foobar')
        creds = {'login': 'phred@example.com', 'password': 'foobar'}

        self.assertEqual(view(creds),
                         {'userid': 'phred','login': 'phred@example.com'})

    def test___call___direct_pas_miss(self):
        view = self._makeOne()
        view.context.acl_users = self._makePAS('phred',
                                                'phred@example.com', 'foobar')
        creds = {'login': 'phred@example.com', 'password': 'bazbam'}

        self.assertEqual(view(creds), {})

    def test___call___non_pas_miss(self):
        view = self._makeOne()
        class NonPAS:
            def _getOb(self, key, default=None):
                return default
        view.context.acl_users = NonPAS()
        creds = {'login': 'phred@example.com', 'password': 'bazbam'}

        self.assertEqual(view(creds), {})

    def test___call___nested_pas_hit_direct(self):
        parent = self._makeContext()
        parent.acl_users = self._makePAS('phred2',
                                         'phred@example.com', 'quxxy')

        context = self._makeContext(parent)
        context.acl_users = self._makePAS('phred',
                                          'phred@example.com', 'foobar')

        view = self._makeOne(context)

        creds = {'login': 'phred@example.com', 'password': 'foobar'}

        self.assertEqual(view(creds),
                         {'userid': 'phred','login': 'phred@example.com'})

    def test___call___nested_pas_hit_parent(self):
        parent = self._makeContext()
        parent.acl_users = self._makePAS('phred2',
                                         'phred@example.com', 'quxxy')

        context = self._makeContext(parent)
        context.acl_users = self._makePAS('phred',
                                          'phred@example.com', 'foobar')

        view = self._makeOne(context)

        creds = {'login': 'phred@example.com', 'password': 'quxxy'}

        self.assertEqual(view(creds),
                         {'userid': 'phred2','login': 'phred@example.com'})

    def test___call___nested_pas_miss(self):
        parent = self._makeContext()
        parent.acl_users = self._makePAS('phred2',
                                         'phred@example.com', 'quxxy')

        context = self._makeContext(parent)
        context.acl_users = self._makePAS('phred',
                                          'phred@example.com', 'foobar')

        view = self._makeOne(context)

        creds = {'login': 'phred@example.com', 'password': 'bamalama'}

        self.assertEqual(view(creds), {})
