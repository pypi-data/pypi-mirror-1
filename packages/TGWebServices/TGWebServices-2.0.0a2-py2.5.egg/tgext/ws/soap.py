"""Implements the SOAP protocol. Specifically, this implementation talks in
the wrapped document/literal form."""

import re
import sys
import traceback
import time
import logging
import datetime

import mimetypes

from peak.rules import abstract, when

try:
    from xml.etree import cElementTree as et
except ImportError:
    import cElementTree as et

from genshi.builder import tag, Element, Namespace

from tg import request, response

from tg import expose, validate, override_template
from formencode import validators

from tgext.ws.runtime import primitives, ctvalues, typedproperty, unsigned
from tgext.ws import iconv

log = logging.getLogger("tgext.ws.soap")

namespace_expr = re.compile(r'^\{.*\}')

mimetypes.add_type("text/xml", ".wsdl")

_simplevalues = set([int, long, float])
_strvalues = set([basestring, str, unicode])

@abstract()
def soap_value(name, return_type, value):
    """Converts a value into xml Element objects for inclusion in the
    SOAP response output."""
    pass

@when(soap_value, "type(value) in _strvalues")
def xml_string(name, return_type, value):
    elem = Element(name, **{"xsi:type" : "xsd:string"})
    elem(value)
    return elem
 
@when(soap_value, "type(value) in _simplevalues")
def soapint(name, return_type, value):
    elem = Element(name, **{"xsi:type" : soap_type(return_type)})
    elem(str(value))
    return elem

@when(soap_value, "isinstance(value, bool)")
def soapbool(name, return_type, value):
    elem = Element(name, **{"xsi:type" : "xsd:boolean"})
    elem(str(value).lower())
    return elem

@when(soap_value, "type(value) not in primitives")
def soap_instance(name, return_type, value):
    """Handles an instance of a complex type."""
    elem = Element(name, **{"xsi:type" : value.__class__.__name__})
    cls = value.__class__
    for key in ctvalues(cls):
        elem.append(soap_value(key, getattr(cls, key),
                    getattr(value, key)))
    return elem

@when(soap_value, "isinstance(value, list)")
def soap_list(name, return_type, value):
    # in the context of the SOAP output, the types: namespace is implied
    elem = Element(name, **{"xsi:type" : 
            soap_type(return_type).replace("types:", "")})
    itemtype = soap_type(return_type)
    for item in value:
        elem.append(soap_value("item", itemtype, item))
    return elem

def soap_body(methodname, function_info, output):
    """Generates xml Elements for the body of a SOAP response."""
    body = Element(methodname + "Response")
    body.append(soap_value("result", function_info.return_type, output['result']))
    return body


# Maps Python types to XML Schema types
type_registry = {
    basestring : "xsd:string",
    str : "xsd:string",
    unicode : "xsd:string",
    int : "xsd:int",
    long : "xsd:long",
    float : "xsd:float",
    bool : "xsd:boolean",
    unsigned : "xsd:unsignedInt"
}

# Maps python types to appropriately named array types.
array_registry = {
    basestring : "String_Array",
    str : "String_Array",
    unicode : "String_Array",
    int : "Int_Array",
    long : "Long_Array",
    float : "Float_Array",
    bool : "Boolean_Array",
}

def handle_list(kind, arrays):
    """Figures out what kind of array the user has declared and registers
    that type. Arrays need to be declared separately in the XML schema."""
    # check for primitive types
    if kind in array_registry:
        arraytype = array_registry[kind]
    elif not isinstance(kind, type):
        return handle_list(kind.__class__, arrays)
    else:
        arraytype = kind.__name__ + "_Array"
    if arrays is not None:
        arrays.add(kind)
    return arraytype
        

def soap_type(kind, arrays=None):
    """Figures out an appropriate schema declaration for the object that is 
    passed in."""
    if kind is None:
        return "xsd:string"
    
    if isinstance(kind, typedproperty):
        return soap_type(kind.type, arrays)
        
    if isinstance(kind, list):
        try:
            return "types:" + handle_list(kind[0], arrays)
        except IndexError:
            raise IndexError("Cannot determine SOAP data type from empty list")
    if kind in type_registry:
        return type_registry.get(kind)
    if not isinstance(kind, type):
        return soap_type(kind.__class__, arrays)
    return "types:" + kind.__name__

class DummyValidator(object):
    def validate(self, params, state):
        return params

class SoapController(object):
    """Controller that manages the SOAP requests and responses. This also
    provides the api.wsdl URL that describes the web service."""
    def __init__(self, wscontroller, tns, typenamespace):
        self.wscontroller = wscontroller
        self.arrays = None
        self.tns = tns
        self.typenamespace = typenamespace


    
    @expose('genshi:tgext.ws.templates.soap_fault')
    def client_error_handler(self, *args, **kw):
        from pylons import tmpl_context
        errors = tmpl_context.form_errors
        faultstring = errors.get('_the_form')
        if faultstring is None:
            faultstring = ', '.join("%s: %s" % (key, value) for key, value in errors.items())
        response.status = "500 Invalid Input"
        return dict(fault_code="Client", 
            fault_string="%s"%faultstring,
            fault_time=datetime.datetime.now().isoformat(),
            fault_method=request.soap_method,
            fault_has_traceback=False,
            )

    @expose('genshi:tgext.ws.templates.soap_fault')
    def server_error_handler(self, faultstring, debuginfo):
        response.status = "500 Internal Server Error"

        return dict(fault_code="Server", 
            fault_string="%s"%faultstring,
            fault_time=datetime.datetime.now().isoformat(),
            fault_method=request.soap_method,
            fault_has_traceback=False,
            )

    @expose("genshi:tgext.ws.templates.soap",
              content_type="application/soap+xml;charset=utf-8")
    @validate(validators=DummyValidator(), error_handler=client_error_handler)
    def index(self):
        """Processes SOAP requests and generates the responses."""
        # get request data and produce an ElementTree that we can work with.
        #request = request
        #response = response
        clen = int(request.headers.get('Content-Length')) or 0
        data = request.body
        request.soap_start = data[:2048]
        soapreq = et.fromstring(data)

        # find the body of the request and the specific method name that has
        # been requested.
        body = soapreq.find("{http://schemas.xmlsoap.org/soap/envelope/}Body")
        body = body.getchildren()[0]
        methodname = body.tag
        methodname = namespace_expr.sub("", methodname)
        request.soap_method = methodname

        try:
            method = self.wscontroller._ws_funcs[methodname]
        except KeyError, e:
            raise validators.Invalid("Unknown SOAP method: %s" %
                                     methodname, methodname, None)
        
        # ensure that the requested method has actually been exposed
        deco = getattr(method, "decoration", None)
        assert hasattr(deco, "exposed") and deco.exposed == True and hasattr(deco, '_ws_func_info')

        input_types = method.decoration._ws_func_info.input_types
        params = iconv.handle_xml_params(body, input_types)
        
        # set the _tgws flag so that the TurboGears wrapping is not applied
        # in wsexpose. We want to manage the produced dictionary here, because
        # we need to pass additional information on to the soap template.
        output = method(**params)
        if not 'result' in output:
            response.status = "500 Internal Server Error"
            try:
                override_mapping = request._override_mapping
            except AttributeError:
                override_mapping = request._override_mapping = {}
            override_mapping[self.index.im_func] = {
                'application/soap+xml;charset=utf-8': [
                    'genshi',
                    'tgext.ws.templates.soap_fault',
                     []
                ]}

            return dict(fault_code="Server", 
                fault_string="%s"%output.get('faultstring'),
                fault_time=datetime.datetime.now().isoformat(),
                fault_method=request.soap_method,
                fault_has_traceback=False,
                )
        data = dict(baseURL=self.wscontroller._ws_baseURL,
                    tns=self.tns,
                    typenamespace=self.typenamespace,
                    soap_body=soap_body, output=output,
                    methodname=methodname, 
                    function_info =
                        self.wscontroller._ws_funcs[methodname].decoration._ws_func_info)
        return data
    
    @expose("genshi:tgext.ws.templates.wsdl",
              content_type="text/xml; charset=utf-8")
    def api(self, xmlsoap=False):
        """Produces the WSDL for this SOAP service."""
        if self.arrays is None:
            self._initialize_arrays()
        ct = list(self.wscontroller._ws_complex_types)
        ct.sort(key=lambda item: (item._type_dependents, item.__name__),
                reverse=True)
        funclist = self.wscontroller._ws_funcs.keys()
        funclist.sort()
        
        # Apache Axis2 demands the w3.org namespace for soapenc
        # Axis1 needs the xmlsoap variety.
        if xmlsoap:
            soapenc = "http://schemas.xmlsoap.org/soap/encoding/"
        else:
            soapenc = "http://www.w3.org/2001/09/soap-encoding"
        return dict(service_name=self.wscontroller.__class__.__name__,
                    baseURL=self.wscontroller._ws_baseURL,
                    registry=self.wscontroller._ws_funcs, soap_type=soap_type,
                    funclist=funclist,
                    soap_array=handle_list,
                    complex_types=ct,
                    ctvalues=ctvalues,
                    arrays=self.arrays, soapenc=soapenc,
                    tns=self.tns, typenamespace=self.typenamespace)
    
    @expose("genshi:tgext.ws.templates.wsdl",
              content_type="text/xml; charset=utf-8")
    def xmlsoap_wsdl(self):
        return self.api_wsdl(xmlsoap=True)
    
    def _initialize_arrays(self):
        arrays = set()
        for func in self.wscontroller._ws_funcs.values():
            soap_type(func.decoration._ws_func_info.return_type, arrays)
            for type in func.decoration._ws_func_info.input_types.values():
                soap_type(type, arrays)
        for cls in self.wscontroller._ws_complex_types:
            for key in ctvalues(cls):
                soap_type(getattr(cls, key), arrays)
        self.arrays = arrays
