"""Tests for HTTP+XML services"""

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
