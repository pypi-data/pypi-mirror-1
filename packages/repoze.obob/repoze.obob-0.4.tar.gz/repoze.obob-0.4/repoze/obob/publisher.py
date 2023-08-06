import sys
""" repoze.obob publisher:  perform policy-driven graph traversal.
"""

class DefaultHelper:
    """ Default traversal policy helper.

    Simple applications may just use this class directly.  More complex
    apps can either subclass it, or else supply a different 'helper_factory'
    to the ObobPublisher constructor, implementing all the same methods
    on the returned object.
    """
    def __init__(self, environ, **extras):
        """ Initialize helper.

        @param object environ      WSGI environment
        @param dict extras         Extra application configuration
        """
        self.environ = environ
        self.extras = extras.copy()
        path_info = self.environ.get('PATH_INFO', '')
        self.names = [x for x in path_info.split('/') if x.strip()]
        self.names.reverse()

    def setup(self):
        """ Perform any initializtion require before request processing.
        
        @return None
        """
        pass

    def next_name(self):
        """ Return the name of the next element to find
        
        @return string element       Path element
        """
        if self.names:
            return self.names.pop()

    def before_traverse(self, current):
        """ Called before traversing each path element.
        
        @param object current       Object being traversed
        @return None
        """
        pass

    def traverse(self, current, name):
        """ Traverse the next path element.
        
        @param object current       Object being traversed
        @param object name          Name of next object
        @return object              Next object in traversal chain
        """
        return current[name]

    def before_invoke(self, published):
        """ Called just before invoking the published object.
        
        @param object publishe      Published object (end of traversal chain)
        @return None
        """
        pass

    def invoke(self, published):
        """ Invoke the published object.
        
        @param object publishe      Published object (end of traversal chain)
        @return object              Result of call
        """
        return published()

    def map_result(self, result):
        """ Map the call result onto a triple for WSGI.
        
        @param object result        Result of calling published object
        @return tuple               WSGI triple: (status, headers, body_iter)
        """
        if isinstance(result, basestring):
            result = [result]
        return '200 OK', [('Content-Type', 'text/html')], result

    def teardown(self):
        """ Perform any cleanup required end of request processing
        
        @return None
        """
        pass

    def handle_exception(self, exc_info):
        """ Handle any exceptions that happen during helper consultation.
        Reraise or return a WSGI triple.
        
        @return tuple               WSGI triple: (status, headers, body_iter)
        """
        t, v, tb = exc_info
        try:
            raise t, v, tb
        finally:
            del tb

class ObobPublisher:
    """ repoze graph-traversal publisher.

    o Plug points include a callable to find the root object for traversal,
      plus one to return a traversal policy helper.
    """
    def __init__(self,
                 initializer=None,
                 helper_factory=None,
                 get_root=None,
                 dispatchable=None,
                 extras=None,
                ):

        if helper_factory is not None:
            self.helper_factory = helper_factory

        if get_root is not None:
            self.get_root = get_root
        else:
            if dispatchable is None:
                dispatchable = {}
            self._default_root = _DefaultRoot(dispatchable)

        if extras is None:
            extras = {}

        self.extras = extras

        if initializer is not None:
            initializer(**extras)

    def __call__(self, environ, start_response):
        """ Application dispatch via graph traversal.

        0. Construct a traversal policy helper.

        1. Get traversal root via self.get_root().

        2. Iterate over items in request's path:

           a. Notify 'self.before_traverse' if not None.

           b. Get next object via 'self.traverse'.

        3. Notify 'self.before_invoke', if not None.

        4. Call the terminal ("published") object, applying request
           parameters.

        5. Map result onto WSGI 'start_response' + iteration.
        """
        helper = self.helper_factory(environ, **self.extras)
        try:
            try:
                helper.setup()
                root = current = self.get_root(helper)

                while 1:
                    helper.before_traverse(current)
                    name = helper.next_name()
                    if name is None:
                        break
                    current = helper.traverse(current, name)

                published = current

                helper.before_invoke(published)
                result = helper.invoke(published)

                status, headers, body_iter = helper.map_result(result)

            except:
                exc_info = sys.exc_info()
                status, headers, body_iter = helper.handle_exception(exc_info)

            start_response(status, headers)
            return body_iter

        finally:
            helper.teardown()
                

    def get_root(self, helper):
        return self._default_root

    def helper_factory(self, environ, **kw):
        return DefaultHelper(environ, **kw)

    def initializer(self):
        pass

class _DefaultRoot:
    """ Default root object, configured as a callable mapping.
    """
    def __init__(self, dispatchable):
        self._dispatchable = dispatchable

    def keys(self):
        return self._dispatchable.keys()

    def __getitem__(self, key):
        return self._dispatchable[key]

    def __call__(self, *args, **kw):
        lines = ['<html>',
                 '<body>',
                 '<ul>',
                ]
        keys = self._dispatchable.keys()
        keys.sort()
        for key in keys:
            lines.append('<li><a href="%s">%s</a></li>' % (key, key))
        lines.extend(['</ul>',
                      '</body>',
                      '</html>',
                     ])
        return lines


_PLUGPOINTS = ('get_root',
               'helper_factory',
               'initializer',
              )

def _resolve(dotted_or_ep):
    """ Resolve a dotted name or setuptools entry point to a callable.
    """
    from pkg_resources import EntryPoint
    return EntryPoint.parse('x=%s' % dotted_or_ep).load(False)

def make_obob(global_config, **kw):
    """ WSGI application factory.
    """
    PREFIX = 'repoze.obob.'
    dispatchable = {}
    extras = {}
    new_kw = {'dispatchable': dispatchable, 'extras': extras}
    merged = global_config.copy()
    merged.update(kw)
    for k, v in merged.items():
        if k.startswith(PREFIX):
            trimmed = k[len(PREFIX):]
            callable = _resolve(v)
            if trimmed in _PLUGPOINTS:
                new_kw[trimmed] = callable
            else:
                dispatchable[trimmed] = callable
        else:
            extras[k] = v
    return ObobPublisher(**new_kw)
