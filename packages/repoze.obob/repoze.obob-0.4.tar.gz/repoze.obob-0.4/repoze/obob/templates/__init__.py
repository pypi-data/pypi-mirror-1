import os
import sys

from paste.script import templates
from paste.script.templates import var

import pkg_resources

pastescriptv = pkg_resources.get_distribution('PasteScript').version.split('.')
if pastescriptv <= ['1', '3', '6']:
    # pastescript 1.3.6 has a bug in should_skip_file when a 'CVS' directory
    # exists in the skeldir (missing name pad)
    def should_skip_file(name):
        """
        Checks if a file should be skipped based on its name.

        If it should be skipped, returns the reason, otherwise returns
        None.
        """
        if name.startswith('.'):
            return 'Skipping hidden file %(filename)s'
        if name.endswith('~') or name.endswith('.bak'):
            return 'Skipping backup file %(filename)s'
        if name.endswith('.pyc'):
            return 'Skipping .pyc file %(filename)s'
        if name in ('CVS', '_darcs'):
            return 'Skipping version control directory %(filename)s'
        return None
    from paste.script import copydir
    copydir.should_skip_file = should_skip_file

class NewBobTemplate(templates.Template):
    _template_dir = 'newbob_skel'
    summary = "A project with a namespace package"
    required_templates = []
    use_cheetah = False
    
    vars = [
        var('package', 'Package name'),
        var('version', 'Version', default='0.1'),
        var('description', 'One-line description of the package'),
        var('long_description', 'Multi-line description (in reST)'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('keywords', 'Space-separated keywords/tags'),
        var('url', 'URL of homepage'),
        var('license_name', 'License name', default='ZPL'),
        ]
