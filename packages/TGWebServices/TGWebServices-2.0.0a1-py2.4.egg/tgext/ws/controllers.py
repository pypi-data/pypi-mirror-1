# Web Services controllers
"""Handles the Controller part of MVC for web services. This provides the
WebServicesController class which is the main entry point for people wanting
to use web services."""

import logging
import types
import re
import sys
import traceback

try:
#    # python 2.5 ?
    from xml.etree import cElementTree as et
except ImportError:
#    # python 2.4 ? so try to get stand-alone version
    import cElementTree as et

import pylons

from genshi.builder import tag, Element

import tg
from tg.decorators import Decoration
from pylons import config
from formencode import validators
from tg.controllers import TGController

from tgext.ws import iconv
from tgext.ws import soap
from tgext.ws import xml_
from tgext.ws import json

from tgext.ws.runtime import register, primitives, \
                                  FunctionInfo, register_complex_type, \
                                  ctvalues

#app_config.update({"tg.empty_flash" : False})

# TODO find a better place to initialize the render_functions
config['render_functions']['wsautoxml'] = xml_.render_autoxml
config['render_functions']['wsautojson'] = json.render_autojson

log = logging.getLogger("tgwebservices.controller")

def dict_wrapped_result(func):
    """Wraps a call to a function so that the return value is put into a
    single item dictionary, with the key 'result'.
    
    @param func Function to wrap
    @return a new function
    """
    def d_w_r(*args, **kw):
        try:
            d = dict(result=func(*args, **kw))
        except Exception, e:
            excinfo = sys.exc_info()
    
            d = dict(faultcode="Server",
                     faultstring=str(excinfo[1]),
                     debuginfo="\nTraceback:\n%s\n" % 
                               "\n".join(traceback.format_exception(
                                                   *excinfo)))
    
        return d
    d_w_r.__name__ = func.__name__
    d_w_r.__doc__ = func.__doc__
    d_w_r.decoration = func.decoration
    return d_w_r

_wrong_parameters = re.compile(r".*\(\) takes .* \(\d+ given\)")
_unexpected_parameters = re.compile(r".*\(\) got an unexpected keyword "
                                    "argument .*")
class wsexpose(object):
    def __init__(self, return_type=None):
        self.return_type = return_type

    def __call__(self, func):

        fi = register(func)
        func = dict_wrapped_result(func)

        fi.return_type = self.return_type
        func = tg.expose(template='wsautoxml:', content_type='text/xml')(func)
        func = tg.expose(template='wsautojson:', content_type='application/json')(func)

        self.fi = fi

        deco = Decoration.get_decoration(func)
        #deco.register_hook('before_call', self.before_call)
        deco.validation = Validation(fi)

        if isinstance(self.return_type, list):
            rt = self.return_type[0]
            if rt not in primitives:
                register_complex_type(fi, rt)
        elif self.return_type not in primitives:
            register_complex_type(fi, self.return_type)

        return func

class Validation(object):
    class Validators(object):
        def __init__(self, fi):
            self.fi = fi

        def validate(self, params, state):
            jsonp = params.pop('jsonp', None)

            if "tg_format" in params:
                if params["tg_format"] == "json":
                    pylons.request.response_type = "application/json"
                else:
                    pylons.request.response_type = "text/xml"
                del params["tg_format"]
                
            if pylons.request.response_type is None and \
                    pylons.request.headers.get("Content-Type", None) is not None:
                content_type = pylons.request.headers.get("Content-Type")
                if content_type.startswith("application/json") or \
                        content_type.startswith("text/javascript"):
                    pylons.request.response_type = "application/json"
                elif content_type.startswith("text/xml"):
                    pylons.request.response_type = "text/xml"
            
            request = pylons.request
            input_types = self.fi.input_types

            if "_xml_request" in params:
                try:
                    data = params["_xml_request"]
                    body = et.fromstring(data)
                except SyntaxError:
                    raise validators.Invalid("Request XML is invalid", "",
                                             None)
                params.clear()
                params.update(iconv.handle_xml_params(body, input_types))

            elif "_json_request" in params:
                json_request = params["_json_request"]
                params.clear()
                params.update(iconv.handle_json_params(json_request, input_types))
            elif request.headers.get("Content-Type", "").startswith("text/xml"):
                try:
                    clen = int(request.headers.get('Content-Length')) or 0
                    data = request.body
                    body = et.fromstring(data)
                except SyntaxError:
                    raise validators.Invalid("Request XML is invalid", "", 
                                             None)
                params.clear()
                params.update(iconv.handle_xml_params(body, input_types))
            elif request.headers.get("Content-Type", "").startswith("application/json"):
                clen = int(request.headers.get('Content-Length')) or 0
                data = request.body
                params.clear()
                params.update(iconv.handle_json_params(data, input_types))
            else:
                iconv.handle_keyword_params(params, input_types)

            if jsonp:
                from pylons import tmpl_context
                tmpl_context.jsonp = jsonp

            return params
    def __init__(self, fi):
        self.validators = Validation.Validators(fi)

    @tg.expose('wsautoxml:', content_type='text/xml')
    @tg.expose('wsautojson:', content_type='application/json')
    def error_handler(self, *args, **kwargs):
        from pylons import tmpl_context
        errors = tmpl_context.form_errors
        faultstring = errors.get('_the_form')
        if faultstring is None:
            faultstring = ', '.join("%s: %s" % (key, value) for key, value in errors.items())
        return dict(faultcode="Client", 
            faultstring="%s"%faultstring)

class wsvalidate(object):
    def __init__(self, *types, **kwtypes):
        self.types = types
        self.kwtypes = kwtypes

    def __call__(self, func):
        deco = Decoration.get_decoration(func)
        fi = register(func)
        input_types = dict()

        for i, argtype in enumerate(self.types):
            input_types[fi.params[i]] = argtype

        input_types.update(self.kwtypes)
            

        # Make sure all of the input types are registered
        # so they show up in the WSDL.
        for argname, argtype in input_types.items():
            if isinstance(argtype, list):
                typetoreg = argtype[0]
            else:
                typetoreg = argtype
            if typetoreg not in primitives:
                log.info('registering complex type %s for %s',
                         typetoreg, argname)
                register_complex_type(fi, typetoreg)

        fi.input_types = input_types

        return func

class WebServicesController(object):
    """A controller that implements a piece of a web services API."""
    
    def _ws_gather_functions_and_types(self, prefix):
        """Collects all of the functions and types on this controller and the
        controllers beneath it."""
        funcs = dict()
        complex_types = set()
        for key in dir(self):
            if key.startswith("_"):
                continue
            item = getattr(self, key)

            # functions are globally registered with Java-style
            # camelCase names
            if prefix:
                newname = prefix+key[0].upper()+key[1:]
            else:
                newname = key
            
            # check for functions and sub-controllers
            if hasattr(item, "_ws_gather_functions_and_types"):
                morefuncs, moretypes = \
                            item._ws_gather_functions_and_types(newname)
                funcs.update(morefuncs)
                complex_types.update(moretypes)
            elif isinstance(item, types.MethodType):
                deco = getattr(item, 'decoration', None)
                if hasattr(deco, "_ws_func_info"):
                    funcs[newname] = item
                    complex_types.update(deco._ws_func_info.complex_types)
        return funcs, complex_types
        
class WebServicesRoot(TGController, WebServicesController):
    """The root of a mu]lti-protocol web service."""

    def __init__(self, baseURL=None, tns=None, typenamespace=None):
        """Constructor for a WebServicesRoot controller.
        
        @param baseURL Sets the URL path for this controller. Some protocols
            need to know this.
        @param tns The SOAP target namespace (defaults to baseURL+soap/)
        @param typenamespace the namespace for the SOAP types (defaults to
            baseURL+soap/types)
        """
        baseURL = baseURL or pylons.config.get('ws.baseURL', '')
        if not baseURL.endswith('/'):
            baseURL += '/'
        if not tns:
            tns = baseURL + "soap/"
        if not typenamespace:
            typenamespace = tns + "types"
        self._ws_baseURL = baseURL
        self._ws_parent = None
        self.soap = soap.SoapController(self, tns, typenamespace)
        self._ws_funcs, self._ws_complex_types = \
            self._ws_gather_functions_and_types("")

