import pylons

import turbojson

def render_autojson(template_name, template_vars, **kw):
    jsonp = template_vars['c'].jsonp

    if 'faultcode' in template_vars:
        result = dict(
            faultcode=template_vars.get('faultcode'),
            faultstring=template_vars.get('faultstring'))
        if 'debuginfo' in template_vars:
            result['debuginfo']=template_vars.get('debuginfo')
    else:
        result = dict(result=template_vars['result'])
    result = turbojson.jsonify.encode(result)

    if jsonp:
        result = '%s(%s);' % (jsonp, result)

    return result
