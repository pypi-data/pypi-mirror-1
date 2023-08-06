#!/usr/bin/env python

from distutils.core import setup

documentation = """
PyTin is a CGI framework that provides shortcuts for application writers to
focus less on common tasks and more on their application's functionality.

Requests
========
Requests take all the data that exists in different areas like environment
variables and standard input, and puts it all into one, cleanly organized
object.

Responses
=========
Responses are file-like objects, but with convenience methods named ``w`` (with
a newline) and ``wn`` (without one). They also have custom attributes for
setting common HTTP headers like ``Content-Type`` and ``Location``.

RQMods/RSMods
=============
These are applied to requests and responses. You pass a list of them as the
``rqmods`` and ``rsmods`` keyword arguments. They're not required, and PyTin
doesn't even ship with any (yet), but they could be very helpful if you're in
a situation where you'd need one.

Bake
====
Bake is the major function you need to know. It will publish your object,
collect the environment variables, enable tracebacks if needed, and pass extra
settings to your application. After your request has been returned, it will be
compiled and returned.

Prebake
=======
The prebake function is designed to allow extra security and lighter script
files. It's a command-line-based wizard that produces a simple file that imports
a function stored in a module and automatically bakes it.
"""

setup(name='PyTin',
      version='1.1',
      author='LeafStorm/Pacific Science',
      author_email='pacsciadmin@gmail.com',
      url='http://pac-sci.homeip.net/index.cgi/swproj/pytin',
      description='A CGI environment framework.',
      long_description=documentation,
      py_modules=['pytin'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.5',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
                   ],
      requires=['iotk'],
      provides=['pytin'])
