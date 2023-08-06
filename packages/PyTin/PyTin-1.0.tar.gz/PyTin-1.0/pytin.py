#!/usr/bin/env python
"""
PyTin
=====
This is PyTin, the Python CGI Helper framework. Its goal is to provide
shortcuts for CGI scriptwriters to get more done.

The most important function provided by PyTin is the ``bake`` function. Full
details are in ``bake``'s docs, but all you need to know to get started is
that ::
    
    pytin.bake(cgiexec)

will call ``cgiexec(request_object)`` (in production mode, as opposed to debug).

In addition, if you type ``python -m pytin``, you can "Prebake" a script that
will run an application stored in a module.

:version: 1.0
:license: GNU General Public License
"""

import cgi
import re
import os
import string
import Cookie
import cgitb
import urllib
from iotk import *
from UserDict import UserDict
from StringIO import StringIO

def getenv(name):
    if name in os.environ:
        return os.environ[name]
    else:
        return None

class URLDict(UserDict):
    """
This class adds ONE thing to UserDict, and that is the ``__str__()`` function's
behavior, which will add all the parts in order. The default parts are:
    
- ``host``: The server name.
- ``port``: The port the server is running on.
- ``script``: The path to the script.
- ``path``: The extra path info after the script name.
- ``query``: The query string.
    """
    def __str__(self):
        temp = ""
        if ('host' in self.data) and ('port' in self.data):
            temp += (self.data['host'] + ":" + self.data['port'])
        elif (host in self.data):
            temp += self.data['host']
        else:
            pass
        temp += self.data['script']
        if 'path' in self.data:
            temp += self.data['path']
        if 'query' in self.data:
            temp += self.data['query']
        return temp

class AutoRequest:
    """
AutoRequest is a class that will, upon instantiation, stuff itself with all the
CGI data needed to start and run an application. It will include:

``rqmethod`` : string
    This is the name of the method used to make the CGI request. Under *most*
    circumstances, it will be ``GET`` or ``POST``, but don't take it for
    granted.
``fields`` : ``cgi.FieldStorage``
    This can be accessed in a dict-like manner to get the fields from the query
    string or that were POSTed. See the ``cgi`` module docs for more info.
``cookie`` : ``Cookie.SimpleCookie``
    This is another dictionary-like object. Again, see the ``Cookie`` module
    docs for more info.
``url`` : ``URLDict``
    This is an instance of a special dictionary included in this module.
``client`` : dictionary
    This is a vanilla dictionary. It has information regarding the person who
    is visiting your site, in the keys ``ip`` (the IP address), ``agent`` (the
    user-agent string), ``referrer`` (the page they just visited), and 
    ``authname`` (if HTTP authentication is used, the username).
``settings`` : dictionary
    If keyword arguments are passed to the AutoRequest, they are stored in
    ``settings``.
    """
    def __init__(self, settings = {}):
        self.settings = settings
        
        self.rqmethod = getenv('REQUEST_METHOD')
        self.fields = cgi.FieldStorage()
        self.client = {}
        
        if getenv("HTTP_COOKIE"):
            self.cookie = Cookie.SimpleCookie(getenv("HTTP_COOKIE"))
        else:
            self.cookie = None
        
        self.url = URLDict()
        if getenv("HTTP_HOST"):
            self.url['host'] = getenv("HTTP_HOST")
        if getenv("SERVER_PORT"):
            self.url['port'] = getenv("SERVER_PORT")
        self.url['script'] = getenv("SCRIPT_NAME")
        if getenv("PATH_INFO"):
            self.url['path'] = getenv("PATH_INFO")
        if getenv("QUERY_STRING"):
            self.url['query'] = getenv("QUERY_STRING")
        
        self.client['ip'] = getenv("REMOTE_ADDR")
        self.client['agent'] = getenv("HTTP_USER_AGENT")
        if getenv("HTTP_REFERER"):
            self.client['referrer'] = getenv("HTTP_REFERER")
        if getenv("REMOTE_USER"):
            self.client['authname'] = getenv("REMOTE_USER")

class Response(StringIO):
    """
This class handles the sending side of the relationship. The first thing a
good app should do is create a ``Response`` instance, preferably named ``r``.
The last thing it should do is return the ``Response``.

The most important thing you can do to a response is write to it. You do this
with the ``w(text)`` method. Note that this will append a newline. If you don't
want a newline to be appended, use ``wn(text)``. You'll also probably need to
set these important attributes.

``ctype``
    The default value for this is ``text/html``. You can change it if you want
    to send out something that's not HTML.
``cookie``
    If ``cookie`` is set, it should be something from the ``Cookie`` module.
    This will be sent to the client in the HTTP headers.
``extra_headers``
    A dictionary. This is a collection of extra headers (the key is the header
    name) to write to the response.
``redirect``
    This is the same thing as ``extra_headers['Location']``, just shorter. It's
    a URL that the browser should redirect to upon receiving the response.
``attachment``
    If you want to have the enclosed data sent as an attachment, set this to
    the desired filename.
    """
    ctype = "text/html"
    cookie = None
    extra_headers = {}
    redirect = None
    attachment = False
    response = ""
    
    def w(self, text):
        self.write(text + "\n")
    
    def wn(self, text):
        self.write(text)
    
    def compile_response(self):
        self.response =  ""
        self.response += "Content-Type: "
        self.response += self.ctype
        self.response += "\n"
        
        if self.cookie:
            self.response += str(self.cookie)
            self.response += "\n"
        
        if self.redirect:
            self.response += "Location: "
            self.response += self.redirect
            self.response += "\n"
        
        if self.attachment:
            self.response += "Content-Disposition: attachment; filename="
            self.response += self.attachment
            self.response += "\n"
        
        if self.extra_headers:
            for key, value in self.extra_headers.items():
                self.response += key
                self.response += ": "
                self.response += value
                self.response += "\n"
        
        self.response += "\n"
        self.response += self.getvalue()
        return self.response

def makelink(request, path="", **getargs):
    """
Makes a link. You pass it a request object, and it uses the information to make
a link. You can have a path and pass keyword arguments to it.
    """
    if path:
        if not getargs:
            return request.url['script'] + "/" + path
        else:
            return request.url['script'] + "/" + path + "?" + urllib.urlencode(getargs)
    elif getargs:
        return request.url['script'] + "?" + urllib.urlencode(getargs)
    else:
        return request.url['script']

def bake(publish, debug=False, rqmods=[], rsmods=[], **kwargs):
    """
Bake is a very simple function for serving PyTin scripts. It goes through this 
process:

#. First, it checks to see if the script is running as CGI or something else.
  Currently, if it's something else, the script will exit, but in the future,
  a testing system may be added.
#. Then, it checks if ``debug`` is True. If so, it will switch on the ``cgitb``
   module, causing tracebacks to appear in the browser.
#. After that, it will make an ``AutoRequest``. If any functions were specified
  in ``rqmods`` (they should be in a list, even if there's only one), they will
  be passed the request and do something with it if they like.
#. The baked callable will be executed now, being passed the modified request.
  It should return a response.
#. If any mods are specified in a list in ``rsmods``, they will be called with
  the response and return it back modified.
#. Finally, the response will be compiled and returned.
    """
    if not getenv("REQUEST_METHOD"):
        print "This isn't a CGI environment!"
        return
    if debug:
        cgitb.enable()
    if kwargs:
        settings = kwargs
    else:
        settings = {}
    rq = AutoRequest(settings)
    if rqmods:
        for mod in rqmods:
            rq = mod(rq)
    response = publish(rq)
    if rsmods:
        for mod in rsmods:
            response = mod(response)
    response.compile_response()
    print response.response
    return


def generate_script(a): # a: Just a random, short name
    sb = StringIO() # sb: Script Buffer
    sb.write('#!/usr/bin/env python\n')
    sb.write('"""\n')
    sb.write('Application launcher for ')
    sb.write(a['name'])
    sb.write("\nGenerated by PyTin 1.0 Prebake\n")
    sb.write('"""\n')
    sb.write('from pytin import bake\n')
    sb.write('from ')
    sb.write(a['module'])
    sb.write(' import ')
    sb.write(a['item'])
    sb.write('\n\n')
    sb.write('if __name__ == "__main__":\n')
    sb.write('    bake(')
    sb.write(a['item'])
    if a['call']:
        sb.write('()')
    if a['debug']:
        sb.write(', debug=True')
    if 'options' in a:
        for key, value in a['options'].items():
            sb.write(', ')
            sb.write(key)
            sb.write('=')
            sb.write(value)
    sb.write(')')
    sb.seek(0)
    return sb.read()


def prebake():
    print_string("PyTin 1.0 Prebake", just="c")
    print_string("=================", just="c")
    print_string("Prebake will take an application stored in a module and " + \
        "create a small script that will run it.")
    a = dict()
    a['name'] = ask_string("What is the application's name?")
    a['module'] = ask_string("What module is the application stored in?")
    a['item'] = ask_string("What is the name of the class/function/method that runs the app?")
    a['call'] = ask_yes_no("If this is a class, does it need to be instantiated first?")
    print
    print_string("You can enable debug mode now. This will make tracebacks appear in the" + \
        " browser, which is good during development but bad in production. If you want to " + \
        " enable it now and disable it later, you'll need to edit the script later.")
    a['debug'] = ask_yes_no("Should the debug mode be activated?")
    print
    if ask_yes_no("Do you want to set extra options for the application?"):
        a['options'] = dict()
        while True:
            key = ask_string("What is the setting name?")
            print_string("What is the setting's value?")
            value = ask_string("(Put quotes around it if it's a string.)")
            a['options'][key] = value
            if not ask_yes_no("Do you want to add another option?"):
                break
            else:
                print
    filename = ask_string("What file should I save the script in?")
    script = generate_script(a)
    print
    print script
    if ask_yes_no("Is this script OK?"):
        try:
            scriptfile = open(filename, 'w')
            scriptfile.write(script)
            print_string("Succeeded in clobbering " + filename + " and writing the script to it.")
        except IOError:
            print_string("That didn't work. You might have a permissions problem.")


if __name__ == "__main__":
    prebake()
