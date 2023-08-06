"""A template plugin that generates simple XML"""
from genshi.builder import Element

from peak.rules import abstract, when

from tgext.ws.runtime import primitives, ctvalues, typedproperty

_simplevalues = set([int, long, float, bool])
_strvalues = set([basestring, str, unicode])

@abstract()
def xml_value(name, value):
    """Converts a value into XML Element objects."""
    pass

@when(xml_value, "type(value) in _strvalues")
def xml_string(name, value):
    elem = Element(name)
    elem(value)
    return elem
 
@when(xml_value, "type(value) in _simplevalues")
def xml_simple(name, value):
    elem = Element(name)
    elem(str(value))
    return elem

@when(xml_value, "type(value) not in primitives")
def xml_instance(name, value):
    """Handles an instance of a complex type."""
    elem = Element(name)
    cls = value.__class__
    for key in ctvalues(cls):
        elem.append(xml_value(key, getattr(value, key)))
    return elem

@when(xml_value, "isinstance(value, list)")
def xml_list(name, value):
    elem = Element(name)
    for item in value:
        elem.append(xml_value("item", item))
    return elem

@when(xml_value, "isinstance(value, dict)")
def xml_dict(name, value):
    elem = Element(name)
    for key in value.keys():
        if key.startswith("tg_"):
            continue
        elem.append(xml_value(key, value[key]))
    return elem

def render_autoxml(template_name, template_vars, **kwargs):
    if "faultcode" in template_vars:
        result = dict(
            faultcode = template_vars.get('faultcode'),
            faultstring = template_vars.get('faultstring'))
        if 'debuginfo' in template_vars:
            result['debuginfo'] = template_vars.get('debuginfo')
    elif "result" not in template_vars:
        template_vars = dict(result=template_vars)
    else:
        result = template_vars['result']
    return str(xml_value("result", result))


