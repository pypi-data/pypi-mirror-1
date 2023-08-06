from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1237928867.1548631
_template_filename='/home/mehtap/frla/frla/templates/form3.mako'
_template_uri='/form3.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        # SOURCE LINE 1
        context.write(u'<body text="#ffffff" bgcolor="#000000" vlink="#ff0000" link="#aa0000">\n<form name="test" method="GET" action="/dbayar/ayarla">\nHost: <input type="text" name="host" />\n<input type="submit" name="ayarla" value="Ayarla" />\n</form>\n</body>')
        return ''
    finally:
        context.caller_stack.pop_frame()


