from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1227526258.339103
_template_filename='/home/mehtap/frla/frla/templates/deneme.mako'
_template_uri='/deneme.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['title']


def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        # SOURCE LINE 1
        context.write(u'\n')
        # SOURCE LINE 2
        context.write(unicode(c.ken))
        context.write(u' \n')
        return ''
    finally:
        context.caller_stack.pop_frame()


def render_title(context):
    context.caller_stack.push_frame()
    try:
        # SOURCE LINE 1
        context.write(u'Ken')
        return ''
    finally:
        context.caller_stack.pop_frame()


