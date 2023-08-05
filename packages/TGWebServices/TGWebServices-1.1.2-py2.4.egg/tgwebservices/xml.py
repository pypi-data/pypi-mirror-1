"""A template plugin that generates simple XML"""
from genshi.builder import Element

import dispatch

from tgwebservices.runtime import primitives, ctvalues, typedproperty

_simplevalues = set([int, long, basestring, str, unicode, float, bool])

@dispatch.generic()
def xml_value(name, value):
    """Converts a value into XML Element objects."""
    pass

@xml_value.when("type(value) in _simplevalues")
def xml_simple(name, value):
    elem = Element(name)
    elem(str(value))
    return elem

@xml_value.when("type(value) not in primitives")
def xml_instance(name, value):
    """Handles an instance of a complex type."""
    elem = Element(name)
    cls = value.__class__
    for key in ctvalues(cls):
        elem.append(xml_value(key, getattr(value, key)))
    return elem

@xml_value.when("isinstance(value, list)")
def xml_list(name, value):
    elem = Element(name)
    for item in value:
        elem.append(xml_value("item", item))
    return elem

@xml_value.when("isinstance(value, dict)")
def xml_dict(name, value):
    elem = Element(name)
    for key in value.keys():
        if key.startswith("tg_"):
            continue
        elem.append(xml_value(key, value[key]))
    return elem

class AutoXMLTemplate(object):

    def __init__(self, extra_vars_func=None, options=None):
        pass

    def load_template(self, templatename):
        "There are no actual templates with this engine"
        pass

    def render(self, info, format="html", fragment=False, template=None):
        "Renders the template to a string using the provided info."
        if "result" not in info:
            info = dict(result=info)
        return str(xml_value("result", info["result"]))

    def get_content_type(self, user_agent):
        return "text/xml"