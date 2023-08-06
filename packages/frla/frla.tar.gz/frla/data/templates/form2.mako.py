from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1237982232.357892
_template_filename='/home/mehtap/frla/frla/templates/form2.mako'
_template_uri='/form2.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        g = context.get('g', UNDEFINED)
        # SOURCE LINE 1
        context.write(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n\n<script type="text/javascript">  \n\nfunction get_url_param(name)\n{ \nname = name.replace(/[\\[]/,"\\\\\\[").replace(/[\\]]/,"\\\\\\]"); \nvar regexS = "[\\\\?&]"+name+"=([^&#]*)"; \nvar regex = new RegExp( regexS ); \nvar results = regex.exec( window.location.href ); \nif( results == null )    return ""; \nelse return results[1];\n}\nvar adres = get_url_param(\'adres\');\nvar secenek = get_url_param(\'secenek\')\n</script> \n\n<body text="#ffffff" bgcolor="#000000" vlink="#ff0000" link="#aa0000">\n')
        # SOURCE LINE 19
        context.write(unicode(g.homepage))
        context.write(u'\n<br>\n<script type="text/javascript">\nif (secenek==0){\ndocument.write(\'<h3><font color="ff0000">Configuration of Network Attached Storage Name</font></h3><br>\')\ndocument.write(\'<form name="ekle" method="POST" action="/nasconf/ekleme">\')\ndocument.write(\'Address: <input type="text" name="adres" value="\'+adres+\'"> \')\ndocument.write(\'Name: <input type="text" name="isim" /> \')\ndocument.write(\'<input type="submit" name="ekle" value="   Add   " /></form>\')\n\nif (adres==""){ \ndocument.write(\'<form name="degistir" method="POST" action="/nasconf/degistirme">Address: <input type="text" name="adres" /> Name: <input type="text"name="isim" /> <input type="submit" name="degistir" value="Modify" /></form>\')\ndocument.write(\'<form name="sil" method="POST" action="/nasconf/silme">Address: <input type="text" name="adres" /> Name: <input type="text" name="isim" /> <input type="submit" name="sil" value="Delete" /></form>\')\ndocument.write("*For deleting, it\'s enough to fill only one field.<br>")\n} \ndocument.write(\'<br><form name="listele" method="POST" action="/nasconf/listele">\')\ndocument.write(\'Listing: <input type="submit" name="listele" value="List" /></form>\')\n}\nelse if (secenek==1){\ndocument.write(\'<h3><font color="ff0000">Database Connection Setup</font></h3><br>\')\ndocument.write(\'<form name="dbdeger" method="POST" action="/dbayar/ayarla">\')\ndocument.write(\'<table><tr><td>Database Name:</td><td><input type="text" name="vtisim" /></td></tr>\')\ndocument.write(\'<tr><td>Host:</td><td><input type="text" name="host" /></td></tr>\')\ndocument.write(\'<tr><td>User:</td><td><input type="text" name="kullanici" /></td></td>\')\ndocument.write(\'<tr><td>Password:</td><td><input type="password" name="parola" /></td></tr>\')\ndocument.write(\'<tr align="center"><td colspan=2><input type="submit" name="submit" value="Save" /></td></tr></table>\')\ndocument.write(\'<INPUT TYPE="hidden" NAME="dil" VALUE="en"></form>\')\n}\n</script>\n</body> \n')
        return ''
    finally:
        context.caller_stack.pop_frame()


