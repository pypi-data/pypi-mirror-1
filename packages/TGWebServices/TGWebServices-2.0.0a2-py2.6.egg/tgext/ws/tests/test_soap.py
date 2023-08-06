
try:
    # python >= 2.5
    from xml.etree import cElementTree as et
except ImportError:
    import cElementTree as et

from tgext.ws.tests import TestController

from tgext.ws import soap, runtime

class TestSOAP(TestController):
    def run_soap(self, root, method, params=""):
        request = """<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">

  <soap:Body xmlns="http://foo.bar.baz/soap/">
    <%(method)s>
        %(params)s
    </%(method)s>
  </soap:Body>

</soap:Envelope>
""" % dict(method=method, params=params)

        response = self.app.post("%s/soap/" % root, request,
            headers={"Content-Length" : str(len(request)),
                     "Content-Type" : 
                            "application/soap+xml; charset=utf-8"},
            expect_errors=True)
        self.response = response
        return response.body

    def get_wsdl(self, root):
        output = self.app.get("%s/soap/api.wsdl" % root).body
        print output
        return output

    def test_basic_call(self):
        output = self.run_soap('/myservice', "times2", "<value>5</value>")
        print output
        root = et.fromstring(output)
        result_elements = list(root.findall(".//{http://foo.bar.baz/soap/types}result"))
        print result_elements
        assert len(result_elements) == 1, "Should only have one result"
        elem = result_elements[0]
        print "result:", elem
        assert elem.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == \
            "xsd:int", "Expected result to be labeled an int"
        assert elem.text == "10", "Expected result to be 10"

    def test_wsdl_with_ints(self):
        response = self.app.get("/myservice/soap/api.wsdl")
        output = response.body
        print output
        print response.headers["Content-Type"]
        assert response.headers["Content-Type"] == "text/xml; charset=utf-8"
        root = et.fromstring(output)
        schema_elements = root.findall(".//{http://www.w3.org/2001/XMLSchema}element")
        found = False
        for elem in schema_elements:
            print "FE:", elem
            if "name" in elem.attrib and elem.attrib["name"] == "times2Response":
                found = True
                interior_elem = elem[0][0][0]
                print "response value: %s (%s)" % (interior_elem, 
                                                   interior_elem.attrib)
                assert elem[0][0][0].attrib["type"] == "xsd:int"
        assert found, "Should have found a definition for times2Response"

    def test_wsdl_with_complex(self):
        response = self.app.get("/complex/soap/api.wsdl")
        output = response.body

        print output
        root = et.fromstring(output)
        schema_elements = root.findall(
                                ".//{http://www.w3.org/2001/XMLSchema}element")
        found = False
        for elem in schema_elements:
            if "name" in elem.attrib and elem.attrib["name"] == \
                    "getfancyResponse":
                found = True
                interior_elem = elem[0][0][0]
                print "response value: %s (%s)" % (interior_elem, 
                                                   interior_elem.attrib)
                assert elem[0][0][0].attrib["type"] == "types:FancyValue"
        
        complex_types = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}complexType")
        assert found, "Should have found a definition for fancyResponse"
        
        found = False
        found_array = False
        for elem in complex_types:
            if "name" in elem.attrib and elem.attrib["name"] == \
                            "FancyValue":
                found = True
                objattributes = elem[0].getchildren()
                found_name = False
                found_age = False
                found_computed = False
                for attr in objattributes:
                    if attr.attrib["name"] == "name":
                        assert attr.attrib["type"] == "xsd:string"
                        found_name = True
                    elif attr.attrib["name"] == "age":
                        assert attr.attrib["type"] == "xsd:int"
                        found_age = True
                    elif attr.attrib["name"] == "computed":
                        assert attr.attrib["type"] == "xsd:string"
                        found_computed = True
                    else:
                        assert False, "Found a %s element which shouldn't "\
                                "be there" % (attr.attrib["name"])
                assert found_name, "Did not find name element"
                assert found_age, "Did not find age element"
                assert found_computed, "Did not find computed element"
            elif "name" in elem.attrib and elem.attrib["name"] == \
                "FoodItem_Array":
                found_array = True
        assert found, "Should have found a delcaration for FancyValue"
        assert found_array, "Should have found the FoodItem_Array"

    def test_soap_array(self):
        response = self.app.get("/complex/soap/api.wsdl")
        output = response.body
        print output
        root = et.fromstring(output)
        schema_elements = root.findall(
                                ".//{http://www.w3.org/2001/XMLSchema}complexType")
        found = False
        stringarray_found = False
        for elem in schema_elements:
            if "name" in elem.attrib and elem.attrib["name"] == \
                    "FancyValue_Array":
                found = True
                interior_elem = elem[0]
                assert interior_elem.tag == \
                    "{http://www.w3.org/2001/XMLSchema}sequence", \
                    "Expected to find a sequence in FancyValue_Array"
                interior_elem = interior_elem[0]
                assert interior_elem.tag == \
                    "{http://www.w3.org/2001/XMLSchema}element", \
                    "Expected to find element in FancyValue_Array"
                print interior_elem.attrib
                assert interior_elem.attrib["maxOccurs"] == \
                    "unbounded", "expected unbounded array"
                assert interior_elem.attrib["nillable"] == \
                    "true", "Array should be nillable"
                assert interior_elem.attrib["type"] == \
                    "types:FancyValue", \
                    "Should have found array type declaration of FancyValue"
            if "name" in elem.attrib and elem.attrib["name"] == \
                    "String_Array":
                stringarray_found = True
                interior_elem = elem[0][0]
                assert interior_elem.tag == \
                    "{http://www.w3.org/2001/XMLSchema}element", \
                    "Expected to find element in String_Array"
                print interior_elem.attrib
                assert interior_elem.attrib["type"] == \
                    "xsd:string", \
                    "Should have found string type for String_Array"
        
        assert found, "Expected to find the FancyValiue_Array type"
        assert stringarray_found, "Expected to find the String_Array type"
        
        output = self.run_soap("/complex", "somestrings")
        root = et.fromstring(output)
        print "SOAP somestrings call output:", output
        result_elements = list(root.findall(".//{http://foo.bar.baz/soap/types}result"))
        assert len(result_elements) == 1
        items = result_elements[0].getchildren()
        assert len(items) == 3, "Expected three items in the array"
        assert items[0].text == "A"
        assert items[1].text == "B"
        assert items[2].text == "C"

    def test_nested_complex(self):
        from fixtures.root import FoodItem

        response = self.app.get('/complex/soap/api.wsdl')
        output = response.body
        print "WSDL:\n\n"
        print output
        root = et.fromstring(output)
        schema_elements = root.findall(
                                ".//{http://www.w3.org/2001/XMLSchema}complexType")
        found = False
        for elem in schema_elements:
            if "name" in elem.attrib and elem.attrib["name"] == "FoodOrder":
                found = True
                elements = elem.getchildren()[0].getchildren()
                assert len(elements) == 2
                foundarray = False
                for e in elements:
                    if e.attrib["type"] == "types:FoodItem_Array":
                        foundarray = True
                assert foundarray, "Should have found array of FoodItems"
        assert found, "Should have found FoodOrder type"
        output = self.run_soap("/complex", "getorder")
        print "\n\nSOAP:\n\n"
        print output
        assert '<item xsi:type="FoodItem">' in output
        root = et.fromstring(output)
        persontags = root.findall(".//{http://foo.bar.baz/soap/types}person")
        assert len(persontags) > 0
        assert FoodItem._type_dependents == 1

    def test_complex_types_stay_in_one_controller(self):
        output = self.get_wsdl('/local')
        print "WSDL:\n\n"
        print output
        root = et.fromstring(output)
        schema_elements = root.findall(
                                ".//{http://www.w3.org/2001/XMLSchema}complexType")
        for elem in schema_elements:
            assert not ("name" in elem.attrib and elem.attrib["name"] == "FoodOrder"), \
                "Complex type definitions should be limited to controllers that use them"

    def test_nested_controllers(self):
        output = self.get_wsdl("/outer")
        print "WSDL:\n\n"
        print output
        root = et.fromstring(output)
        schema_elements = root.findall(
                                ".//{http://www.w3.org/2001/XMLSchema}complexType")
        found = False
        for elem in schema_elements:
            if "name" in elem.attrib and elem.attrib["name"] == \
                            "FancyValue":
                found = True
        assert found, "Should have found FancyValue from the nested controller"
        operations = set(["ultimatequestion", "innerGetFancy", "innerFooGetFancy",
                          "anotherGetFancy"])
        porttype = root.findall(".//{http://schemas.xmlsoap.org/wsdl/}portType")[0]
        op_elements = porttype.findall(
                              ".//{http://schemas.xmlsoap.org/wsdl/}operation")
        for elem in op_elements:
            name = elem.attrib["name"]
            assert name in operations, "Found unexpected op %s in WSDL" % (name)
            operations.remove(name)
        assert not operations, "Did not find these ops: %s" % (operations)
        
    def test_call_to_nested_controller(self):
        output = self.run_soap("/outer", "innerFooGetFancy")
        print output
        assert """<innerFooGetFancyResponse><result xsi:type="FancyValue"><age xsi:type="xsd:int">42</age><computed xsi:type="xsd:string">Hello!</computed><name xsi:type="xsd:string">Mr. Bean</name></result></innerFooGetFancyResponse>""" in output

    def test_documentation_strings(self):
        output = self.get_wsdl("/myservice")
        print "WSDL:\n\n"
        print output
        root = et.fromstring(output)
        porttype = root.findall(".//{http://schemas.xmlsoap.org/wsdl/}portType")[0]
        operation = porttype.getchildren()[0]
        assert operation.attrib["name"] == "sum"
        docelems = operation.findall(
                    ".//{http://schemas.xmlsoap.org/wsdl/}documentation")
        print docelems
        assert len(docelems) == 1
        assert docelems[0].text == "Sum all the values"

    def test_boolean_type(self):
        elem = soap.soap_value("test", bool, True)
        output = str(elem)
        print output
        assert output == '<test xsi:type="xsd:boolean">true</test>'

    def test_big_number(self):
        elem = soap.soap_value("test", int, 3063485326L)
        output = str(elem)
        assert output == '<test xsi:type="xsd:int">3063485326</test>'

    def test_empty_list(self):
        output = self.run_soap('/complex', 'getempty')
        print output
        assert "fault" not in output
        assert '<result xsi:type="FancyValue_Array"></result>' in output

    def test_subclass_complex_types_should_appear_in_wsdl(self):
        output = self.get_wsdl('/complex')
        root = et.fromstring(output)
        schema_elements = root.findall(
                                ".//{http://www.w3.org/2001/XMLSchema}complexType")
        foundperson = False
        for elem in schema_elements:
            if "name" in elem.attrib and elem.attrib["name"] == "SubFood":
                for child in elem.getchildren()[0].getchildren():
                    if child.attrib["name"] == "person":
                        foundperson = True
                        print "SubFood person type is %s" % child.attrib["type"]
                        assert child.attrib["type"] == "types:FancyValue", \
                                  "SubFood person should be a FancyValue"
        assert foundperson, "Should have found the person attribute on SubFood"

    def test_unsigned_integer(self):
        output = self.get_wsdl('/complex')
        root = et.fromstring(output)
        schema_elements = root.findall(
                                ".//{http://www.w3.org/2001/XMLSchema}complexType")
        founditem = False
        for elem in schema_elements:
            if "name" in elem.attrib and elem.attrib["name"] == "FoodItem":
                for child in elem.getchildren()[0].getchildren():
                    if child.attrib["name"] == "quantity":
                        founditem = True
                        print "FoodItem quantity type is %s" % child.attrib["type"]
                        assert child.attrib["type"] == "xsd:unsignedInt"
        assert founditem, "Should have found FoodItem's quantity field"
        elem = soap.soap_value("quantity", runtime.unsigned, 5)
        assert str(elem) == '<quantity xsi:type="xsd:unsignedInt">5</quantity>'


    def test_explicit_namespace(self):
        output = self.get_wsdl('/namespaced')
        print output
        assert 'targetNamespace="http://foo.bar/service/URI/"' in output
        assert 'xmlns:types="http://foo.bar/service/URI/types"' in output


    def test_optional(self):
        output = self.get_wsdl('/optionalparams')
        print output
        root = et.fromstring(output)
        schema_elements = root.findall(
                                ".//{http://www.w3.org/2001/XMLSchema}element")
        for elem in schema_elements:
            if elem.attrib.get("name", None) == "addem":
                complextype = elem.getchildren()[0]
                sequence = complextype.getchildren()[0]
                num1 = sequence.getchildren()[0]
                assert num1.attrib["name"] == "num1"
                assert "minOccurs" not in num1.attrib
                num2 = sequence.getchildren()[1]
                assert num2.attrib["name"] == "num2"
                assert num2.attrib["minOccurs"] == "0"
                num3 = sequence.getchildren()[2]
                assert num3.attrib["name"] == "num3"
                assert num3.attrib["minOccurs"] == "0"

    def test_empty_parameter_is_empty_string(self):
        output = self.run_soap("/string", "say_hello", """<name></name>""")
        print output
        assert "fault" not in output

    def test_complex_input_simple_object(self):
        output = self.run_soap("/complexinput", "savePerson", """<p>
        <name>George</name>
        <age>280</age>
    </p>""")
        print output
        from fixtures.root import Person, RootController
        assert isinstance(RootController.complexinput.person, Person)

    def test_rw_typedproperty(self):
        output = self.run_soap("/complex", "getandsetrwprop", """<rwp>
        <value>AValue</value>
    </rwp>""")
        print output
        assert '<getandsetrwpropResponse><result xsi:type="ReadWriteProperty"><value xsi:type="xsd:string">AValue</value></result></getandsetrwpropResponse>' in output

    def test_fault_for_invalid_input(self):
        output = self.run_soap("/myservice", "times2", """<value>whaleblubber</value>""")
        print self.response.status
        print output
        assert self.response.status == "500 Invalid Input"
        root = et.fromstring(output)
        fc = root.findall(".//{http://schemas.xmlsoap.org/soap/envelope/}faultcode")
        assert len(fc) == 1
        assert fc[0].text == 'Client'

        fs = root.findall(".//{http://schemas.xmlsoap.org/soap/envelope/}faultstring")
        assert len(fs) == 1
        assert fs[0].text == "whaleblubber value for the 'value' parameter is not a valid int"

    def test_fault_for_exception(self):
        output = self.run_soap("/myservice", "twentyover", """<value>0</value>""")
        print self.response.status
        assert self.response.status == "500 Internal Server Error"
        print output
        assert "<method>twentyover</method>" in output
        #assert "foo.bar.baz/soap/" in output, "Raw request should be in the fault"
        #assert "return 20 / value" in output, "Traceback should be in fault"
        #assert "ZeroDivisionError" in output, "error should be in fault"

    def test_too_many_arguments(self):
        output = self.run_soap("/complex", "somestrings", "<bogus>value</bogus>")
        print output
        root = et.fromstring(output)
        fc = root.findall(".//{http://schemas.xmlsoap.org/soap/envelope/}faultcode")
        assert len(fc) == 1
        fc = fc[0]
        print "Fault code: ", fc.text
        assert fc.text == "Client"

    def test_bogus_function_gives_client_fault(self):
        output = self.run_soap("/complex", "nonexistentfunction")
        print output
        root = et.fromstring(output)
        fc = root.findall(".//{http://schemas.xmlsoap.org/soap/envelope/}faultcode")
        assert len(fc) == 1
        fc = fc[0]
        print "Fault code: ", fc.text
        assert fc.text == "Client"

