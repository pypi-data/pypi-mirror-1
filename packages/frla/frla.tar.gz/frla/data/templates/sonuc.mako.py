from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1236245989.407865
_template_filename='/home/mehtap/frla/frla/templates/sonuc.mako'
_template_uri='/sonuc.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        # SOURCE LINE 1
        context.write(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n<body text="#ff0000" bgcolor="#000000" link="#ffffff" vlink="#999999" >\n')
        # SOURCE LINE 3
        context.write(unicode(_('anasayfalink')))
        context.write(u'\n')
        # SOURCE LINE 4
        context.write(unicode(_('formmenu')))
        context.write(u'\n<table>\n')
        # SOURCE LINE 6
        for sonuc in c.sonuc:
            # SOURCE LINE 7
            context.write(u'        <tr><td width=100> </td><td>')
            context.write(unicode(sonuc))
            context.write(u'</td></tr>\n')
        # SOURCE LINE 9
        context.write(u'</table>\n</body>')
        return ''
    finally:
        context.caller_stack.pop_frame()


