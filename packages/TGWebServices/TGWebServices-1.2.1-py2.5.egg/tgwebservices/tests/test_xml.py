"""Tests for HTTP+XML services"""

import cStringIO as StringIO

import cherrypy
from turbogears import testutil

from tgwebservices.tests.fixtures import *

def test_simple():
    cherrypy.root = MyService("http://foo.bar.baz")
    testutil.create_request("/times2?value=5")
    output = cherrypy.response.body[0]
    print output
    assert output == """<result>10</result>"""

def test_xml_error():
    testutil.create_request("/times2?value=5&foo=1")
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><faultcode>Client</faultcode><faultstring>foo is not a valid parameter (valid values are: ['value'])</faultstring></result>"""

def test_complex_input():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    request = """<request>
    <person><name>Fred</name><age>22</age></person>
</request>"""
    testutil.create_request("/tenyearsolder", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "text/xml; charset=utf-8"})
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><age>32</age><computed>Hello!</computed>""" \
                     """<name>Fred</name></result>"""

def test_rwproperty():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    request = """<request>
    <rwp><value>AValue</value></rwp>
</request>"""
    testutil.create_request("/getandsetrwprop", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "text/xml; charset=utf-8"})
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><value>AValue</value></result>"""
