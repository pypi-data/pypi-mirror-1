=======
JSONRPC
=======

JSON is javascript object notation. JSON-RPC performs the same service
as XML-RPC, except the transport is JSON instead of XML.

Many thanks to Jim Washington for the work on zif.jsonserver. This project uses
many code writen by Jim. I implemented an additional python JSONRPC proxy which
can communicate with the server. This means we can use this library to call
JSON from python to python. The JSON-RPC proxy uses similar patterns like the
XML-RPC implementation.

There is also an additional xmlhttp and json javascript implementation which
offers a JSON-RPC proxy implementation for JavaScript.

This project provides the proposed request type "application/json". The request
type "application/json-rpc" is supported as long it is not officialy deprecated.

The goal of this project is to provide a JSON-RPC implementation. Simple
Browser views which handle JSON calls with a BrowserRequest are not supported
by this package. I'm still not sure if this is good or bad and in which
direction I will go with this package.

Some of my goals are right now, but can change in the future if I'll understand
all the concepts around JSON, e.g. JSPON, JSONP, CrossSite etc:

- provide a secure way to handle JSON calls from client to server.
  I hope we can implement JSONRequest some days. CrossSite seems to use a
  intereting concept

- Simple pythonic implementation

- Use together with JQuery (see http://www.jquery.org).

- No other dependency then JQuery and basic zope packages.

- well tested (this is not the case for JavaScript right now)


About JSON
----------

See www.json.org for more information about JSON.

See http://json-rpc.org/wd/JSON-RPC-1-1-WD-20060807.html for more information
about the JSON 1.1 specification.


What this package can't do
--------------------------

JSON and this package have different limitations. This package can right now
not handle the following tasks:

- Handle fileupload

- Handle GET request

Note that the JSONRPCRequest implementation is based on the IHTTPRequest, this
means that there is no other browser page available if you call them in
python, e.g. getMultiAdapter((context, request), name='myViewName'). This is
explicitly done this way. If you'd like to use content form such browser pages
in a JSON request/call, you can inherit your skin form IJSONRPCLayer and
IBrowserRequest and register your views for this custom layer.


JSON-RPC server
---------------

The JSON server looks for content-type "application/json", and handles those
requests as JSON-RPC. The official mime-type for JSON is "application/json"
The old content type ``application/json-rpc`` is supported too.

Let's define a content object:

  >>> import zope.interface
  >>> class IDemoContent(zope.interface.Interface):
  ...     """Demo content interface."""

  >>> import persistent
  >>> class DemoContent(persistent.Persistent):
  ...     """Demo content."""
  ...     zope.interface.implements(IDemoContent)

And define a JSONRPC method view:

  >>> from z3c.jsonrpc import publisher
  >>> class DemoView(publisher.MethodPublisher):
  ...     """Sample JSON view."""
  ...
  ...     def hello(self):
  ...         return u"Hello World"
  ...
  ...     def greeting(self, name):
  ...         return u"Hello %s" % name
  ...
  ...     def kwarguments(self, prefix, foo=None, bar=None):
  ...         # Note; keyword arguments can be found in request.form
  ...         return u"%s %s %s" % (prefix, foo, bar)
  ...
  ...     def showId(self):
  ...         return u"The json id is: %s" % self.request.jsonId
  ...
  ...     def forceValueError(self):
  ...         raise ValueError('Something was wrong in server method.')

Let's define a content object that is a container:

  >>> import zope.interface
  >>> class IDemoContainer(zope.app.container.interfaces.IReadContainer):
  ...     """Demo container interface."""

  >>> import persistent
  >>> from zope.app.container import btree

  >>> class DemoContainer(btree.BTreeContainer):
  ...     """Demo container."""
  ...     zope.interface.implements(IDemoContainer)

And define a JSONRPC method view:

  >>> from z3c.jsonrpc import publisher
  >>> class DemoContainerView(publisher.MethodPublisher):
  ...     """Sample JSON view."""
  ...
  ...     def available(self):
  ...         return u"Hello World"
  ...
  ...     def greeting(self, name):
  ...         return u"Hello %s" % name
  ...
  ...     def kwarguments(self, prefix, foo=None, bar=None):
  ...         # Note; keyword arguments can be found in request.form
  ...         return u"%s %s %s" % (prefix, foo, bar)
  ...
  ...     def showId(self):
  ...         return u"The json id is: %s" % self.request.jsonId
  ...
  ...     def forceValueError(self):
  ...         raise ValueError('Something was wrong in server method.')


Make them available under the fake package ``jsonsamples``:

  >>> import sys
  >>> sys.modules['custom'] = type('Module', (), {})()
  >>> sys.modules['custom'].IDemoContent = IDemoContent
  >>> sys.modules['custom'].DemoContent = DemoContent
  >>> sys.modules['custom'].DemoView = DemoView
  >>> sys.modules['custom'].IDemoContainer = IDemoContainer
  >>> sys.modules['custom'].DemoContainer = DemoContainer
  >>> sys.modules['custom'].DemoContainerView = DemoContainerView

Let's show how we can register a jsonrpc view:

  >>> from zope.configuration import xmlconfig
  >>> import z3c.jsonrpc
  >>> context = xmlconfig.file('meta.zcml', z3c.jsonrpc)
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:jsonrpc
  ...       for="custom.IDemoContent"
  ...       class="custom.DemoView"
  ...       permission="zope.Public"
  ...       methods="hello greeting kwarguments showId forceValueError"
  ...       layer="z3c.jsonrpc.testing.IJSONRPCTestSkin"
  ...       />
  ... </configure>
  ... """, context)

Let's show how we can register a jsonrpc view for the container:
(The container class needs permission configuration too)

  >>> context = xmlconfig.file('meta.zcml', z3c.jsonrpc)
  >>> context = xmlconfig.file('meta.zcml', zope.app.component, context)
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c"
  ...     xmlns="http://namespaces.zope.org/zope">
  ...     <class class="custom.DemoContainer">
  ...       <allow
  ...           interface="custom.IDemoContainer"
  ...           />
  ...     </class>
  ...   <z3c:jsonrpc
  ...       for="custom.IDemoContainer"
  ...       class="custom.DemoContainerView"
  ...       permission="zope.Public"
  ...       methods="available greeting kwarguments showId forceValueError"
  ...       layer="z3c.jsonrpc.testing.IJSONRPCTestSkin"
  ...       />
  ... </configure>
  ... """, context)


Now we will setup a content object in our site:

  >>> site  = getRootFolder()
  >>> content = DemoContent()
  >>> site['content'] = content
  >>> container = DemoContainer()
  >>> site['container'] = container

Now we can call the method from our JSONRPC view:

  >>> from z3c.jsonrpc import testing
  >>> request = testing.TestRequest()
  >>> demoView = DemoView(content, request)
  >>> demoView.hello()
  u'Hello World'

But this is not intuitive. Let's see how we can traverse to the method ``hello``
with the traverser:

  >>> from z3c.jsonrpc.publisher import MethodTraverser
  >>> methodTraverser = MethodTraverser(demoView, request)
  >>> methodTraverser.publishTraverse(request, 'hello')()
  u'Hello World'

Now we try to access the JSON-RPC view method with a test browser. As you can
see, there is no view accessible. This is because the JSONRPC view is not a
browser view and is not traversable. The error shows that the request factory
falls back to the browser request factory:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.addHeader('Accept-Language', 'en')
  >>> browser.addHeader('Content-Type', 'application/json')
  >>> siteURL = 'http://localhost/++skin++JSONRPCTestSkin'
  >>> browser.open(siteURL + '/content/hello')
  Traceback (most recent call last):
  ...
  NotFound: Object: <zope.app.folder.folder.Folder...: u'++skin++JSONRPCTestSkin'


Testing
-------

If you need to test a JSONRPC view you can use the test proxy like shown
below in the ``JSON-RPC proxy`` section.


JSON-RPC proxy
--------------

The jsonrpc package provides also a JSON-RPC proxy implementation. This
implementation is similar to the one known from xmlrpclib except that it can
handle JSON instead of XML.

Let's try to call our method called ``hello`` we defined before:

  >>> from z3c.jsonrpc.testing import JSONRPCTestProxy
  >>> proxy = JSONRPCTestProxy(siteURL + '/content')
  >>> proxy.hello()
  u'Hello World'

  >>> p2 = JSONRPCTestProxy(siteURL + '/container')
  >>> p2.available()
  u'Hello World'


Now let's make a remote procedure call with a argument:

  >>> proxy.greeting(u'Jessy')
  u'Hello Jessy'

Now let's make a remote procedure call with a kw arguments. Note that this
key word arguments are stored in the request.form. But this doesn't change
anything because this varaibles are also accessible like form variables e.g.
self.request['foo'].Also note that we don't support the **kw signature:

  >>> proxy.kwarguments('Hello', foo=u'FOO', bar=u'BAR')
  u'Hello FOO BAR'

There is also an ``id`` in the json response. Let's use such a json request id
in our JSONRPCProxy:

  >>> proxy = JSONRPCTestProxy(siteURL + '/content', jsonId = u'my id')
  >>> proxy.showId()
  u'The json id is: my id'

The proxy also knows this id as jsonId:

  >>> proxy.jsonId
  u'my id'

See what happens if the server raises an Exception:

  >>> proxy.forceValueError()
  Traceback (most recent call last):
  ...
  ResponseError: Check proxy.error for error message

and the error message is:

  >>> proxy.error
  u'ValueError: Something was wrong in server method.'

The error property gets reset on the next successfull call:

  >>> x = proxy.showId()
  >>> proxy.error is None
  True

And now we force a ResponseError with a fake JSONReader. But first we
need to replace our IJSONReader utility:

  >>> from z3c.json.interfaces import IJSONReader
  >>> sm = site.getSiteManager()
  >>> fakeJSONReader = testing.ForceResponseErrorJSONReader()
  >>> sm.registerUtility(fakeJSONReader, IJSONReader)

also setup the site hook:

  >>> from zope.app.component import hooks
  >>> hooks.setSite(site)

and just call a method this will now raise a ResponseError:

  >>> proxy = JSONRPCTestProxy(siteURL + '/content')
  >>> proxy.hello()
  Traceback (most recent call last):
  ...
  ResponseError: Unacceptable JSON expression: {"id":"jsonrpc", "method":"hello", "no-params"}

the error message is stored in the proxy too:

  >>> proxy.error
  u'Unacceptable JSON expression: {"id":"jsonrpc", "method":"hello", "no-params"}'


Transport
~~~~~~~~~

We used the JSONRPCTestProxy here for testing. This JSON-RPC proxy is a wrapper
for the original JSONRPCProxy and adds handleErrors support and a special
Transport layer which uses a testing caller. You can use one of the different
Transport layers defined in the z3c.json.transport module in real usecases
together with the default JSONRPCProxy implementation.


cleanup
-------

Now we need to clean up the custom module.

  >>> del sys.modules['custom']
