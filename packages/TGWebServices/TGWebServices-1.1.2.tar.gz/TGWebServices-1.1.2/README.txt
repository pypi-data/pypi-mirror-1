TGWebServices
=============

:Author: Kevin Dangoor <dangoor+tgwebservices@gmail.com>
:Copyright: Copyright 2006, 2007 Kevin Dangoor and Arbor Networks
:License: MIT
:Homepage: http://tgwebservices.python-hosting.com/

.. contents:: Table of Contents

Introduction
------------

TurboGears gives you a plain HTTP with JSON return values API for your
application for free. This isn't always what you want, though. Sometimes,
you don't want to expose all of the data to the web that you need to
render your templates. Maybe you need to support a protocol that names the
function it's calling as part of what it POSTs such as SOAP or XML-RPC.

TGWebServices provides a super simple API for creating web services that
are available via SOAP, HTTP->XML, and HTTP->JSON. The SOAP API generates
WSDL automatically for your Python and even generates enough type
information for statically typed languages (Java and C#, for example) to
generate good client code on their end.

How easy is it?

::

    class Multiplier(WebServicesRoot):

        @wsexpose(int)
        @wsvalidate(int, int)
        def multiply(self, num1, num2):
            return num1 * num2

With this at the root, SOAP clients can find the WSDL file at
/soap/api.wsdl and POST SOAP requests to /soap/. HTTP requests to
/multiply?num1=5&num2=20 will return an XML document with the result of
100. Add ?tg_format=json (or an HTTP Accept: text/javascript header) and
you'll get JSON back.

The great thing about this is that the code above looks like a '''normal
Python function''' and doesn't know a thing about web services.

Prerequisites
-------------

This document assumes a working knowledge of TurboGears.

Features
--------

* Easiest way to expose a web services API
* Supports SOAP, HTTP+XML, HTTP+JSON
* Outputs wrapped document/literal SOAP, which is the most widely
  compatible format
* Provides enough type information for statically typed languages to
  generate conveniently usable interfaces
* Can output instances of your own classes
* Can input instances of your own classes (via SOAP, XML or JSON)
* Works with TurboGears 1.0
* MIT license allows for unrestricted use

Getting Started
---------------

Here is a sample from tgwebservices/tests/fixtures.py::

    from tgwebservices.controllers import WebServicesRoot, WebServicesController, \
                                          wsexpose, wsvalidate

    from tgwebservices.runtime import typedproperty, unsigned

    class MyService(WebServicesRoot):
        @wsexpose(int)
        @wsvalidate(int)
        def times2(self, value):
            "Multiplies value by two."
            return value * 2
    
        @wsexpose(int)
        @wsvalidate(int)
        def twentyover(self, value):
            "Divides 20 by value"
            return 20 / value

There are several things of interest in the example above.

1. Those are all of the imports that you'll likely need
2. The top level controller must subclass WebServicesRoot. This is
   important, because this provides the /soap URL that is required for
   SOAP access.
3. wsexpose is called with the type that is returned from the method.
4. wsvalidate is called with the types of the parameters. You can specify
   the types positionally (*skipping self*) or as keyword arguments to
   wsvalidate.
5. Unlike when you work with TurboGears proper, you do not need to return
   a dictionary. Just return the value directly.

To instantiate and use your WebServicesRoot (MyService in the example above), you can do something like this:

cherrypy.root = MyService("http://foo.bar.baz/")

The constructor for WebServicesRoot has a required parameter of *baseURL*. This parameter sets the URL path of the web service (which will show up as the web service location in the WSDL). There are two optional parameters that will be derived from the baseURL if you don't provide them. Those parameters are *tns*  and *typenamespace*. *tns* is the target namespace declared in the WSDL (the XML namespace for the SOAP operations). *typenamepsace* is the XML namespace for the types defined in the WSDL. *tns* defaults to *baseURL* + "soap/". *typenamespace* defaults to *tns* + "types".

URLs
----

class InnerService(WebServicesRoot):
    @wsexpose(int)
    def times4(self, num):
    return num * 4

class ServiceRoot(WebServicesRoot):
    inner = InnerService()

    @wsexpose(int)
    def times2(self, num):
    return num * 2

Assume that ServiceRoot is instantiated with a *baseURL* of "http://foo.bar.baz/". Here are URLs that are available:

+----------------------------------+-------------------------------------------+
| URL                              | What is it                                |
+==================================+===========================================+
| http://foo.bar.baz/              | nothing there... you could use standard   |
|                                  | TurboGears expose to put a page there.    |
+----------------------------------+-------------------------------------------+
| http://foo.bar.baz/times2        | HTTP access to the times2 method          |
+----------------------------------+-------------------------------------------+
| http://foo.bar.baz/inner/times4  | HTTP access to the times4 method on       |
|                                  | InnerService                              +
+----------------------------------+-------------------------------------------+
| http://foo.bar.baz/soap/         | URL to POST SOAP requests to              |
+----------------------------------+-------------------------------------------+
| http://foo.bar.baz/soap/api.wsdl | URL to get the WSDL file from             |
+----------------------------------+-------------------------------------------+

SOAP method names are created by taking the URL parts and concatenating and
camelCasing them. In the example above, there will be a "times2" SOAP method,
as you'd expect. The "inner/times4" method will become "innerTimes4" in SOAP.
All of the SOAP methods live in a flat namespace and appear in a single WSDL
file that covers your whole web service.

Lists
-----

When you wish to return an array of items, you can specify this by
creating a list that contains one item: the type of the objects in the
list::

    @wsexpose([str])
    def somestrings(self):
        return ["A", "B", "C"]

Since many web services are consumed by statically typed languages like
Java, lists that are returned as SOAP arrays can only contain *one* type
of object.

Custom Objects
--------------

You can return instances of classes that you create. Whenever you see the
term "complex type", you can think "class". "Complex type" comes from XML
Schema terminology that is used in declaring the properties of the
returned type.

Returning complex types is as easy as returning primitive types. However,
you do need to take an extra step in declaring complex types that you wish
to return. Here is an example::

    class FancyValue(object):
        name = ""
        age = int
    
        def computed(self):
            return "Hello!"
        computed = typedproperty(str, computed)
    
        def __init__(self, name=None, age=None):
            self.name = name
            self.age = age

    class ComplexService(WebServicesRoot):
        @wsexpose(FancyValue)
        def getfancy(self):
            "Returns a fancy value"
            fv = FancyValue()
            fv.name = "Mr. Test"
            fv.age = 33
            return fv

In this example, we've created a class called FancyValue that we want to
return from a web service method. TGWebServices will only return
properties of instances that:

* are declared at the class level (in the example above, name is defined
  as a string and age is defined as an int)
* do not start with _
* are not methods

With these rules, it's easy to store whatever housekeeping data you need
on your objects without exposing that data to the web service.

Once you've defined your class, you can specify it as a return value in
wsexpose just as you would a builtin Python type.

See the next section for information about *typedproperty* which appears
in the example above.

Custom Objects as Input
-----------------------

You can also use your own classes as input to methods::

    class Person(object):
        name = str
        age = int

    class ComplexInput(WebServicesRoot):
        @wsexpose()
        @wsvalidate(Person)
        def savePerson(self, p):
            self.person = p

Using SOAP, it's fairly natural to submit objects as input to methods. For
plain HTTP, it's not as obvious, but it is still quite easy. You can submit
XML (which looks just like the XML output for the same object) or JSON.
For XML, you just POST a document with the content-type of text/xml. For
JSON, you POST a document with the content-type of application/json.

Here is sample JSON to post to /savePerson::

    {"p" : {"name" : "Julius", "age" : 2107}}

The XML is similar::

    <parameters>
        <p>
            <name>Julius</name>
            <age>2107</age>
        </p>
    </parameters>

Extra Types You Can Return
--------------------------

The tgwebservices.runtime defines two additional types that you can
return: unsigned and typedproperty. Python doesn't have an unsigned int
type, but you can use the tgwebservices.runtime.unsigned class to tell the
consumer of your service that you are returning an unsigned integer value.

typedproperty wraps the standard Python property function allowing you to
specify what return type will be coming from your property's getter
method. In the example in the previous section, the "computed" property
will be a string.

Getting Help
------------

Questions about TGWebServices should go to the TurboGears mailing list.

http://groups.google.com/group/turbogears
