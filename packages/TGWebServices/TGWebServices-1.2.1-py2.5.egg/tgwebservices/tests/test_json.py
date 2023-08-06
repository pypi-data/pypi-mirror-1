import cStringIO as StringIO

import cherrypy
from turbogears import testutil

from tgwebservices.controllers import WebServicesRoot, wsexpose, wsvalidate
from tgwebservices.tests.fixtures import *

def test_simple():
    cherrypy.root = MyService("http://foo.bar.baz")
    testutil.create_request("/times2?value=5&tg_format=json")
    output = cherrypy.response.body[0]
    print output
    assert output == """{"result": 10}"""

def test_nested_top():
    cherrypy.root = OuterService("http://foo.bar.baz")
    testutil.create_request("/ultimatequestion", 
                            headers=dict(Accept="application/json"))
    output = cherrypy.response.body[0]
    print output
    assert output == """{"result": 42}"""

def test_complex():
    cherrypy.root = ComplexService("http://foo.bar.baz")
    testutil.create_request("/getfancy?tg_format=json")
    output = cherrypy.response.body[0]
    print output
    assert output == """{"result": {"age": 33, "computed": "Hello!", "name": "Mr. Test"}}"""

def test_complex_property():
    cherrypy.root = ComplexService("http://foo.bar.baz")
    testutil.create_request("/getcomprop?tg_format=json")
    output = cherrypy.response.body[0]
    print output
    assert output == """{"result": {"athing": {"age": 55, "computed": "Hello!", "name": "Arnie"}}}"""

def test_error_handling():
    testutil.create_request("/somestrings?foo=1&tg_format=json")
    output = cherrypy.response.body[0]
    print output
    assert output == """{"faultcode": "Client", "faultstring": "foo is not a valid parameter (valid values are: [])"}"""

class BooleanInput(WebServicesRoot):
    @wsexpose(bool)
    @wsvalidate(bool)
    def gotbool(self, truefalse):
        return truefalse

def test_boolean_input():
    def check(test, expected):
        cherrypy.root = BooleanInput("http://foo.bar.baz/")
        testutil.create_request("/gotbool?tg_format=json&truefalse=%s" % test)
        output = cherrypy.response.body[0]
        print output
        assert output == """{"result": %s}""" % expected
    
    tests = [
        ("False", "false"),
        ("True", "true"),
        ("1", "true"),
        ("0", "false"),
        ("false", "false"),
        ("no", "false"),
        ("T", "true"),
        ("F", "false"),
        ("Y", "true"),
        ("N", "false"),
    ]
    for test in tests:
        yield check, test[0], test[1]

def test_complex_input():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    
    request = """{
        "person" : {"name" : "Fred", "age" : 22}
}"""
    testutil.create_request("/tenyearsolder", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "application/json; charset=utf-8"})
    output = cherrypy.response.body[0]
    print output
    print cherrypy.root.last_person.age
    assert cherrypy.root.last_person.age == 32

def test_rwprop():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    
    request = """{"rwp": {"value": "AValue"}}"""
    testutil.create_request("/getandsetrwprop", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "application/json; charset=utf-8",
                                     "Accept" : 
                                        "application/json"})
    output = cherrypy.response.body[0]
    print output
    assert output == """{"result": {"value": "AValue"}}"""
