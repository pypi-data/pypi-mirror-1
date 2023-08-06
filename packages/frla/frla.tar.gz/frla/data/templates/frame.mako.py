from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1227872439.5756421
_template_filename='/home/mehtap/frla/frla/templates/frame.mako'
_template_uri='/frame.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        # SOURCE LINE 1
        context.write(u'<html>\n  <head>\n    <title>FRLA</title>\n  </head>\n<FRAMESET cols="15%,70%,15%">\n\t<FRAME src="">\n\t<FRAMESET rows="20%,70%,*">\n      \t\t<FRAME src="/WinterWall.jpg">\n\t\t<FRAME src="/sonuc.mako">\n\t\t<FRAME src="">\n  \t</FRAMESET>\n  \t<FRAME src="">\n</FRAMESET>\n</html>')
        return ''
    finally:
        context.caller_stack.pop_frame()


