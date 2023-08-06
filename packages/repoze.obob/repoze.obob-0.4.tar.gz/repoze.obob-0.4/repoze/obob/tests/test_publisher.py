import unittest

class DefaultHelperTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.obob.publisher import DefaultHelper
        return DefaultHelper

    def _makeOne(self, environ=None):
        if environ is None:
            environ = {}
        return self._getTargetClass()(environ)

    def test_next_name_root(self):
        helper = self._makeOne({'PATH_INFO': '/'})
        self.assertEqual(helper.next_name(), None)

    def test_next_name_nonroot(self):
        helper = self._makeOne({'PATH_INFO': '/simple'})
        self.assertEqual(helper.next_name(), 'simple')
        self.assertEqual(helper.next_name(), None)

    def test_next_name_nonroot_with_empty(self):
        helper = self._makeOne({'PATH_INFO': '/one//two'})
        self.assertEqual(helper.next_name(), 'one')
        self.assertEqual(helper.next_name(), 'two')
        self.assertEqual(helper.next_name(), None)

    def test_traverse_default(self):
        helper = self._makeOne()
        d = {'key': 'value'}
        self.assertEqual(helper.traverse(d, 'key'), 'value')

    def test_invoke_default(self):
        helper = self._makeOne()
        called_with = []
        request = object()
        RESULT = object()
        def _published(*args, **kw):
            called_with.append((args, kw))
            return RESULT

        result = helper.invoke(_published)

        self.assertEqual(len(called_with), 1)
        self.assertEqual(called_with[0][0], ())
        self.assertEqual(called_with[0][1], {})
        self.failUnless(result is RESULT)

    def test_map_result_default_result_is_string(self):
        helper = self._makeOne()
        request = object()
        result = '<html/>'

        status, headers, body_iter = helper.map_result(result)

        self.assertEqual(status, '200 OK')
        self.assertEqual(len(headers), 1)
        self.assertEqual(headers[0], ('Content-Type', 'text/html'))
        self.assertEqual(body_iter, [result])

    def test_map_result_default_result_not_string(self):
        helper = self._makeOne()
        request = object()
        result = object()

        status, headers, body_iter = helper.map_result(result)

        self.assertEqual(status, '200 OK')
        self.assertEqual(len(headers), 1)
        self.assertEqual(headers[0], ('Content-Type', 'text/html'))
        self.assertEqual(body_iter, result)

    def test_handle_exception(self):
        class MyException(Exception):
            pass
        helper = self._makeOne()
        exc_info = (MyException, MyException('foo'), None)
        self.assertRaises(MyException, helper.handle_exception, exc_info)

class ObobPublisherTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.obob.publisher import ObobPublisher
        return ObobPublisher

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        from repoze.obob.publisher import _PLUGPOINTS

        obob = self._makeOne()
        klass = self._getTargetClass()

        for plugpoint in _PLUGPOINTS:
            from_instance = getattr(obob, plugpoint).im_func
            from_class = getattr(klass, plugpoint).im_func
            self.failUnless(from_instance is from_class)

    def test_ctor_overrides(self):

        def _gr(environ): pass
        def _hf(): pass

        obob = self._makeOne(get_root=_gr, helper_factory=_hf)

        self.failUnless(obob.get_root is _gr)
        self.failUnless(obob.helper_factory is _hf)

    def test_get_root_default_empty(self):
        obob = self._makeOne()
        environ = object()
        self.assertEqual(obob.get_root(environ).keys(), {}.keys())

    def test_get_root_default_nonempty(self):
        def _baz():
            return 'BAZ'
        dispatchable = {'baz': _baz }
        extras = {'foo': 'bar'}
        obob = self._makeOne(dispatchable=dispatchable, extras=extras)
        environ = object()
        root = obob.get_root(environ)
        self.assertEqual(root.keys(), {'baz': 1}.keys())
        self.assertEqual(root['baz'], _baz)
        self.assertEqual(obob.extras, {'foo': 'bar'})

    def test_helper_factory_default(self):
        obob = self._makeOne()
        environ = {}
        helper = obob.helper_factory(environ)
        for api in ('setup',
                    'next_name',
                    'before_traverse',
                    'traverse',
                    'before_invoke',
                    'invoke',
                    'map_result',
                    'teardown',
                   ):
            getattr(helper, api)

    def test___call__extras_passed_to_helper_factory(self):
        from repoze.obob.publisher import DefaultHelper
        PASSED = []
        EXTRAS = {'foo': 'bar'}
        def _hf(environ, **extras):
            PASSED.append((environ, extras))
            return DefaultHelper(environ, **extras)
        obob = self._makeOne(helper_factory=_hf, extras=EXTRAS)
        environ = {'PATH_INFO': '/'}
        obob(environ, lambda x, y: [])

        self.assertEqual(len(PASSED), 1)
        self.assertEqual(len(PASSED[0]), 2)
        self.failUnless(PASSED[0][0] is environ)
        self.assertEqual(PASSED[0][1], EXTRAS)

    def test___call__default_empty_root(self):
        obob = self._makeOne()
        environ = {'PATH_INFO': '/'}
        started = []
        def _start_response(status, headers):
            started.append((status, headers))

        chunks = obob(environ, _start_response)

        self.assertEqual(len(started), 1)
        self.assertEqual(started[0][0], '200 OK')
        self.assertEqual(started[0][1], [('Content-Type', 'text/html')])

        self.assertEqual(len(chunks), 6)
        self.assertEqual(chunks[0], '<html>')
        self.assertEqual(chunks[1], '<body>')
        self.assertEqual(chunks[2], '<ul>')
        self.assertEqual(chunks[3], '</ul>')
        self.assertEqual(chunks[4], '</body>')
        self.assertEqual(chunks[5], '</html>')

    def test___call__default_empty_nonesuch_raises(self):
        obob = self._makeOne()
        environ = {'PATH_INFO': '/nonesuch'}
        started = []
        def _start_response(status, headers):
            started.append((status, headers))

        self.assertRaises(KeyError, obob, environ, _start_response)

    def test___call__default_nonempty_root(self):
        def _baz():
            return 'BAZ'
        dispatchable = {'baz': _baz }
        obob = self._makeOne(dispatchable=dispatchable)
        environ = {'PATH_INFO': '/'}
        started = []
        def _start_response(status, headers):
            started.append((status, headers))

        chunks = obob(environ, _start_response)

        self.assertEqual(len(started), 1)
        self.assertEqual(started[0][0], '200 OK')
        self.assertEqual(started[0][1], [('Content-Type', 'text/html')])

        self.assertEqual(len(chunks), 7)
        self.assertEqual(chunks[0], '<html>')
        self.assertEqual(chunks[1], '<body>')
        self.assertEqual(chunks[2], '<ul>')
        self.assertEqual(chunks[3], '<li><a href="baz">baz</a></li>')
        self.assertEqual(chunks[4], '</ul>')
        self.assertEqual(chunks[5], '</body>')
        self.assertEqual(chunks[6], '</html>')

    def test___call__default_nonempty_path(self):
        def _baz():
            return 'BAZ'
        dispatchable = {'baz': _baz }
        obob = self._makeOne(dispatchable=dispatchable)
        environ = {'PATH_INFO': '/baz'}
        started = []
        def _start_response(status, headers):
            started.append((status, headers))

        chunks = obob(environ, _start_response)

        self.assertEqual(len(started), 1)
        self.assertEqual(started[0][0], '200 OK')
        self.assertEqual(started[0][1], [('Content-Type', 'text/html')])

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], 'BAZ')

    def test___call__helperfactory_handle_exception_returns(self):
        class NonRaisingHelperFactory:
            t = []
            v = []
            def __init__(self, environ, **kw):
                pass
            def setup(self):
                raise ValueError('i am raising')
            def teardown(self):
                pass
            def handle_exception(self, exc_info):
                t, v  = exc_info[:2]
                self.t.append(t)
                self.v.append(v)
                return '200 OK', (), ['body']
        started = []
        def _start_response(status, headers):
            started.append((status, headers))
        obob = self._makeOne(helper_factory=NonRaisingHelperFactory)
        environ = {'PATH_INFO': '/baz'}
        self.assertEqual(obob(environ, _start_response), ['body'])
        self.assertEqual(len(NonRaisingHelperFactory.t), 1)
        self.assertEqual(NonRaisingHelperFactory.t[0], ValueError)
        self.assertEqual(len(NonRaisingHelperFactory.v), 1)
        self.assertEqual(NonRaisingHelperFactory.v[0].args[0], 'i am raising')
        self.assertEqual(len(started), 1)
        status, headers = started[0]
        self.assertEqual(status, '200 OK')
        self.assertEqual(headers, ())

    def test___call__helperfactory_handle_exception_raises(self):
        class RaisingHelperFactory:
            t = []
            v = []
            def __init__(self, environ, **kw):
                pass
            def setup(self):
                raise ValueError('i am raising')
            def teardown(self):
                pass
            def handle_exception(self, exc_info):
                t, v = exc_info[:2]
                self.t.append(t)
                self.v.append(v)
                raise RuntimeError(v.args[0])
        obob = self._makeOne(helper_factory=RaisingHelperFactory)
        environ = {'PATH_INFO': '/baz'}
        self.assertRaises(RuntimeError, obob, environ, None)
        self.assertEqual(len(RaisingHelperFactory.t), 1)
        self.assertEqual(RaisingHelperFactory.t[0], ValueError)
        self.assertEqual(len(RaisingHelperFactory.v), 1)
        self.assertEqual(RaisingHelperFactory.v[0].args[0], 'i am raising')

