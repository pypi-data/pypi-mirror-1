__version__ = '0.4'

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

setup(name='repoze.obob',
      version=__version__,
      description='Zope-like publisher as WSGI application',
      long_description=README,
      classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='web application server wsgi zope',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      test_suite='repoze.obob.tests',
      tests_require=['PasteScript >= 1.3.6'],
      install_requires=[
              'PasteScript >= 1.3.6',
              'WSGIUtils >= 0.7'
              ],
      entry_points="""
      [paste.app_factory]
      obob = repoze.obob:make_obob
      [paste.paster_create_template]
      newbob = repoze.obob.templates:NewBobTemplate
      """,
      )

