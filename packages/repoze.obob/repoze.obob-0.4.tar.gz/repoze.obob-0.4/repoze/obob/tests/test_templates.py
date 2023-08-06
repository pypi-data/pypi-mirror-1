import os
import shutil
import tempfile
import unittest

class NewBobTemplateTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.obob.templates import NewBobTemplate
        return NewBobTemplate

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_run(self):
        newbob = self._makeOne('newbob')
        dn = tempfile.mkdtemp()
        vars = {}
        for name in ('project', 'package', 'version', 'description',
                     'long_description', 'author', 'author_email', 'keywords',
                     'url', 'license_name'):
            vars[name] = name
        try:
            command = DummyCommand()
            newbob.run(command, dn, vars)
            j = os.path.join
            self.failUnless(os.path.isdir(j(dn, 'package')))
            self.failUnless(os.path.exists(j(dn, 'setup.py')))
            self.failUnless(os.path.exists(j(dn, 'package', '__init__.py')))
            self.failUnless(os.path.exists(j(dn, 'package', 'tests.py')))
        finally:
            shutil.rmtree(dn)

class DummyOptions:
    pass

class DummyCommand:
    verbose = False
    options = DummyOptions()
    options.simulate = False
    options.overwrite = False
    interactive = False

