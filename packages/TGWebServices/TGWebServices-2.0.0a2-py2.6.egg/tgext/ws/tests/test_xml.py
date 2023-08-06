"""Tests for HTTP+XML services"""

from tgext.ws.tests import TestController

class TestXML(TestController):
    def test_simple(self):
        response = self.app.get('/myservice/times2?value=5')
        print response.headers["Content-Type"]
        assert response.headers["Content-Type"] == "text/xml; charset=utf-8"
        output = response.body
        print output
        assert output == """<result>10</result>"""

    def test_xml_error(self):
        response = self.app.get("/myservice/times2?value=5&foo=1")
        output = response.body
        print output
        assert output == """<result><faultcode>Client</faultcode><faultstring>foo is not a valid parameter (valid values are: ['value'])</faultstring></result>"""

    def test_complex_input(self):
        request = """<request>
        <person><name>Fred</name><age>22</age></person>
    </request>"""
        response = self.app.post("/complex/tenyearsolder", request,
                                {"Content-Length" : str(len(request)),
                                         "Content-Type" : 
                                            "text/xml; charset=utf-8"})
        print response.headers["Content-Type"]
        assert response.headers["Content-Type"] == "text/xml; charset=utf-8"
        output = response.body
        print output
        assert output == """<result><age>32</age><computed>Hello!</computed>""" \
                         """<name>Fred</name></result>"""

    def test_complex_input_on_get(self):
        request = """<request><person><name>Fred</name><age>22</age></person></request>"""
        response = self.app.get("/complex/tenyearsolder?tg_format=xml&_xml_request=%s" % request)
        print response.headers["Content-Type"]
        assert response.headers["Content-Type"] == "text/xml; charset=utf-8"
        output = response.body
        print output
        assert output == """<result><age>32</age><computed>Hello!</computed>""" \
                         """<name>Fred</name></result>"""


    def test_complex_params(self):
        person = """<person><name>Fred</name><age>22</age></person>"""
        response = self.app.get("/complex/tenyearsolder?tg_format=xml&person=%s" % person)

        print response.headers["Content-Type"]
        assert response.headers["Content-Type"] == "text/xml; charset=utf-8"
        output = response.body
        print output
        assert output == """<result><age>32</age><computed>Hello!</computed>""" \
                         """<name>Fred</name></result>"""


    def test_rwproperty(self):
        request = """<request>
        <rwp><value>AValue</value></rwp>
    </request>"""
        response = self.app.post("/complex/getandsetrwprop", request, 
                                {"Content-Length" : str(len(request)),
                                         "Content-Type" : 
                                            "text/xml; charset=utf-8"})
        print response.headers["Content-Type"]
        assert response.headers["Content-Type"] == "text/xml; charset=utf-8"
        output = response.body
        print output
        assert output == """<result><value>AValue</value></result>"""
