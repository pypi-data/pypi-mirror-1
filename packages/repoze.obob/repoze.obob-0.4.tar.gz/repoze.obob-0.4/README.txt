Overview

  repoze.obob is a reconstruction of the "bobo" precursor of Zope (the
  "object publisher" portion), stripped down to be used as a possible
  application endpoint in the 'repoze' stack.

Installation

  Installing setuptools

    repoze.obob depends on setuptools for its installation.  To install
    setuptools:

    - Download ez_setup.py from
      http://peak.telecommunity.com/dist/ez_setup.py
  
    - Run ez_setup.py using Python 2.4.3 or better.  You can use
      http://peak.telecommunity.com/dist/virtual-python.py if you're
      running a UNIX system to avoid polluting your "system" Python's
      "site-packages" directory with repoze-required eggs.

  Installing repoze

    - After ez_setup.py is finished installing setuptools, run::

      $pyprefix/bin/python setup.py develop

    This will cause all packages required by repoze.obob to be
    installed as Python eggs in the Python site-packages directory and
    will cause the code from within the repoze.obob directory to be
    used during execution.

Testing

   - To all run repoze.obob tests, cd to the top-level repoze.obob
     checkout dir and run::

      $pyprefix/bin/python setup.py test

