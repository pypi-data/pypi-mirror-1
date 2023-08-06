from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1237981665.6334431
_template_filename='/home/mehtap/frla/frla/templates/form.mako'
_template_uri='/form.mako'
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
        context.write(unicode(g.anasayfalink2))
        context.write(u'\n<br>\n<script type="text/javascript">\nif (secenek==0){\ndocument.write(\'<h3><font color="ff0000">Kablosuz Eri\u015fim Noktalar\u0131n\u0131n \u0130simlerini Yap\u0131land\u0131rma</font></h3><br>\')\ndocument.write(\'<form name="ekle" method="POST" action="/kenyapilandirma/ekleme">\')\ndocument.write(\'Adres: <input type="text" name="adres" value="\'+adres+\'"> \')\ndocument.write(\'\u0130sim: <input type="text" name="isim" /> \')\ndocument.write(\'<input type="submit" name="ekle" value="    Ekle    " /></form>\')\nif (adres==""){ \ndocument.write(\'<form name="degistir" method="POST" action="/kenyapilandirma/degistirme">Adres: <input type="text" name="adres" /> \u0130sim: <input type="text"name="isim" /> <input type="submit" name="degistir" value="Degistir" /></form>\')\ndocument.write(\'<form name="sil" method="POST" action="/kenyapilandirma/silme">Adres: <input type="text" name="adres" /> \u0130sim: <input type="text" name="isim" /> <input type="submit" name="sil" value="     Sil     " /></form>\')\ndocument.write("Silme i\u015flemi i\xe7in tek bir alan\u0131 doldurman\u0131z yeterlidir.<br>")\n}\ndocument.write(\'<br>\')\ndocument.write(\'<form name="listele" method="POST" action="/kenyapilandirma/listele">Listeleme: <input type="submit" name="listele" value="Listele" /></form>\')\n}\nelse if (secenek==1){\ndocument.write(\'<h3><font color="ff0000">Veritaban\u0131 Ba\u011flant\u0131 Ayarlar\u0131</font></h3><br>\')\ndocument.write(\'<form name="dbdeger" method="POST" action="/dbayar/ayarla">\')\ndocument.write(\'<table><tr><td>Veritaban\u0131 Ad\u0131:</td><td><input type="text" name="vtisim" /></td></tr>\')\ndocument.write(\'<tr><td>Host:</td><td><input type="text" name="host" /></td></tr>\')\ndocument.write(\'<tr><td>Kullan\u0131c\u0131:</td><td><input type="text" name="kullanici" /></td></td>\')\ndocument.write(\'<tr><td>Parola:</td><td><input type="password" name="parola" /></td></tr>\')\ndocument.write(\'<tr align="center"><td colspan=2><input type="submit" name="submit" value="Kaydet" /></td></tr></table>\')\ndocument.write(\'<INPUT TYPE="hidden" NAME="dil" VALUE="tr" /></form>\')\n}\n</script> \n</body>')
        return ''
    finally:
        context.caller_stack.pop_frame()


