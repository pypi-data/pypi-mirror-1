"""Tests for HTTP+JSON services"""

from tgext.ws.tests import TestController

import simplejson

class TestJSON(TestController):
    def test_simple(self):
        response = self.app.get("/myservice/times2.json?value=5")
        output = response.body
        print output
        assert output == """{"result": 10}"""

    def test_jsonp(self):
        response = self.app.get("/myservice/times2?value=5&tg_format=json&jsonp=myFunc")
        output = response.body
        print output
        assert output == """myFunc({"result": 10});"""

    def test_simple_array(self):
        response = self.app.get("/myservice/sum?values=5&values=10&tg_format=json")
        output = response.body
        print output
        assert output == """{"result": 15}"""

    def test_nested_top(self):
        response = self.app.get("/outer/ultimatequestion", headers=dict(Accept="application/json"))
        output = response.body
        print output
        assert output == """{"result": 42}"""

    def test_complex(self):
        response = self.app.get("/complex/getfancy?tg_format=json")
        output = response.body
        print output
        assert output == """{"result": {"age": 33, "computed": "Hello!", "name": "Mr. Test"}}"""

    def test_complex_property(self):
        response = self.app.get("/complex/getcomprop?tg_format=json")
        print response.headers["Content-Type"]
        assert response.headers["Content-Type"] == "application/json; charset=utf-8"
        output = response.body
        print output
        assert output == """{"result": {"athing": {"age": 55, "computed": "Hello!", "name": "Arnie"}}}"""

    def test_error_handling(self):
        response = self.app.get("/complex/somestrings?foo=1&tg_format=json")
        output = response.body
        print output
        assert output == """{"faultcode": "Client", "faultstring": "foo is not a valid parameter (valid values are: [])"}"""

    def test_boolean_input(self):
        def check(test, expected):
            output = self.app.get("/boolean/gotbool?tg_format=json&truefalse=%s" % test).body
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
            check(*test)

    def test_complex_input(self):
        request = """{
            "person" : {"name" : "Fred", "age" : 22}
    }"""
        response = self.app.post('/complex/tenyearsolder', request,
                                 headers={"Content-Length" : str(len(request)),
                                          "Content-Type" : 
                                          "application/json; charset=utf-8"})
        output = response.body
        print output
        output = simplejson.loads(output)
        print output['result']['age']
        assert output['result']['age'] == 32

    def test_complex_input_on_get(self):
        request = """{"person":{"name":"Fred","age":22}}"""
        response = self.app.get("/complex/tenyearsolder?tg_format=json&_json_request=%s" % request)

        output = response.body
        print output
        output = simplejson.loads(output)
        print output['result']['age']
        assert output['result']['age'] == 32

    def test_complex_params_on_get(self):
        person = """{"name":"Fred","age":22}"""
        response = self.app.get("/complex/tenyearsolder?tg_format=json&person=%s" % person)
        output = response.body
        print output
        output = simplejson.loads(output)
        print output['result']['age']
        assert output['result']['age'] == 32

    def test_rwprop(self):
        
        request = """{"rwp": {"value": "AValue"}}"""
        response = self.app.post("/complex/getandsetrwprop", request, 
                                headers={"Content-Length" : str(len(request)),
                                         "Content-Type" : 
                                            "application/json; charset=utf-8",
                                         "Accept" : 
                                            "application/json"})
        output = response.body
        print output
        assert output == """{"result": {"value": "AValue"}}"""
