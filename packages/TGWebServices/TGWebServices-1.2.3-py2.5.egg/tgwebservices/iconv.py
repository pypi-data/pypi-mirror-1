"""Input Conversion Routines"""

import re

try:
#    # python 2.5 ?
    from xml.etree import cElementTree as et
except ImportError:
#    # python 2.4 ? so try to get stand-alone version
    import cElementTree as et

import simplejson
from turbogears import validators

from tgwebservices.runtime import primitives, typedproperty

namespace_expr = re.compile(r'^\{.*\}')

def boolean_converter(value):
    value = value.lower()
    if value in ["", "false", "0", "no", "off", "f", "n"]:
        return False
    if value in ["true", "1", "yes", "on", "y", "t"]:
        return True
    raise validators.Invalid("%s is not a legal boolean value" % (value),
                             value, None)

def _get_single_value(elem, itype):
    """Converts a single XML element into the given type"""
    if isinstance(itype, list):
        itemtype = itype[0]
        items = []
        for subelem in elem.getchildren():
            items.append(_get_single_value(subelem, itemtype))
        return items
    if isinstance(itype, typedproperty):
        itype = itype.type
    if not isinstance(itype, type):
        itype = type(itype)
    if itype not in primitives:
        return _xml_to_instance(elem, itype)
    if itype == bool:
        itype = boolean_converter
        
    if elem.text is None:
        text = ""
    else:
        text = elem.text
        
    try:
        return itype(text)
    except ValueError:
        raise validators.Invalid(
            "%s value for the '%s' parameter is not a "
            "valid %s" % (text, namespace_expr.sub("", elem.tag),
                         itype.__name__), 
            text, None)
    
def _xml_to_instance(input, cls):
    """Converts an input element into a new instance of cls."""
    instance = cls()
    for elem in input.getchildren():
        tag = namespace_expr.sub("", elem.tag)
        try:
            itype = getattr(cls, tag)
        except AttributeError:
            raise validators.Invalid("%s is an unknown tag for a %s" 
                                     % (tag, cls.__name__),
                tag, None)
        setattr(instance, tag, _get_single_value(elem, itype))
    return instance

def handle_xml_params(body, input_types):
    kw = {}
    for elem in body.getchildren():
        param = namespace_expr.sub("", elem.tag)
        try:
            itype = input_types[param]
        except KeyError:
            raise validators.Invalid(
                "%s is not a valid parameter (valid values are: %s)"
                % (param, input_types.keys()), param, None
            )
        kw[param] = _get_single_value(elem, itype)
    return kw

def convert_complex_param(value, input_type):
    # For complex type, we expect either json or xml
    # The first character will decide which one we're dealing with
    print value, input_type
    if value.startswith('<'):
        return _get_single_value(et.fromstring(value), input_type)
    elif value.startswith('{'):
        value = simplejson.loads(value)
        return _get_json_value(value, input_type)
    else:
        raise ValueError, value

def convert_param(value, input_type):
    if type(input_type) == list:
        return map(lambda n: convert_param(n, input_type[0]), value)
    elif input_type is bool:
        return boolean_converter(value)
    elif input_type in primitives:
        return input_type(value)
    else:
        return convert_complex_param(value, input_type)

def handle_keyword_params(kw, input_types):
    # convert the input parameters to appropriate types
    for key in kw:
        if key in input_types:
            try:
                kw[key] = convert_param(kw[key], input_types[key])
            except ValueError:
                raise validators.Invalid(
                    "%s value for the '%s' parameter is not a "
                    "valid %s" % (kw[key], key, 
                                 input_types[key].__name__), 
                    kw[key], None)
        else:
            raise validators.Invalid(
                "%s is not a valid parameter (valid values are: %s)"
                % (key, input_types.keys()), key, None
            )

def _get_json_value(value, itype):
    if isinstance(itype, list):
        itemtype = itype[0]
        return [_get_json_value(item, itemtype) for item in value]
    elif isinstance(itype, typedproperty):
        return _get_json_value(value, itype.type)
    elif not isinstance(itype, type):
        return _get_json_value(value, type(itype))
    elif itype not in primitives and isinstance(value, dict):
        return _create_instance_from_json(value, itype)
    return itype(value)

def _create_instance_from_json(value, cls):
    instance = cls()
    for key in value:
        try:
            itype = getattr(cls, key)
        except AttributeError:
            raise validators.Invalid("%s is an unknown parameter for a %s" 
                                     % (key, cls.__name__),
                key, None)
        setattr(instance, str(key), _get_json_value(value[key], itype))
    return instance

def handle_json_params(input, input_types):
    if isinstance(input, basestring):
        try:
            input = simplejson.loads(input)
        except ValueError:
            raise validators.Invalid("Invalid JSON input")
    kw = {}
    for key in input:
        if key in input_types:
            kw[str(key)] = _get_json_value(input[key], input_types[key])
        else:
            raise validators.Invalid(
                "%s is not a valid parameter (valid values are: %s)"
                % (key, input_types.keys()), key, None
            )
    return kw
        
