<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<script type="text/javascript">  

function get_url_param(name)
{ 
name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]"); 
var regexS = "[\\?&]"+name+"=([^&#]*)"; 
var regex = new RegExp( regexS ); 
var results = regex.exec( window.location.href ); 
if( results == null )    return ""; 
else return results[1];
}
var adres = get_url_param('adres');
var secenek = get_url_param('secenek')
</script> 

<body text="#ffffff" bgcolor="#000000" vlink="#ff0000" link="#aa0000">
${g.anasayfalink2}
<br>
<script type="text/javascript">
if (secenek==0){
document.write('<h3><font color="ff0000">Kablosuz Erişim Noktalarının İsimlerini Yapılandırma</font></h3><br>')
document.write('<form name="ekle" method="POST" action="/kenyapilandirma/ekleme">')
document.write('Adres: <input type="text" name="adres" value="'+adres+'"> ')
document.write('İsim: <input type="text" name="isim" /> ')
document.write('<input type="submit" name="ekle" value="    Ekle    " /></form>')
if (adres==""){ 
document.write('<form name="degistir" method="POST" action="/kenyapilandirma/degistirme">Adres: <input type="text" name="adres" /> İsim: <input type="text"name="isim" /> <input type="submit" name="degistir" value="Degistir" /></form>')
document.write('<form name="sil" method="POST" action="/kenyapilandirma/silme">Adres: <input type="text" name="adres" /> İsim: <input type="text" name="isim" /> <input type="submit" name="sil" value="     Sil     " /></form>')
document.write("Silme işlemi için tek bir alanı doldurmanız yeterlidir.<br>")
}
document.write('<br>')
document.write('<form name="listele" method="POST" action="/kenyapilandirma/listele">Listeleme: <input type="submit" name="listele" value="Listele" /></form>')
}
else if (secenek==1){
document.write('<h3><font color="ff0000">Veritabanı Bağlantı Ayarları</font></h3><br>')
document.write('<form name="dbdeger" method="POST" action="/dbayar/ayarla">')
document.write('<table><tr><td>Veritabanı Adı:</td><td><input type="text" name="vtisim" /></td></tr>')
document.write('<tr><td>Host:</td><td><input type="text" name="host" /></td></tr>')
document.write('<tr><td>Kullanıcı:</td><td><input type="text" name="kullanici" /></td></td>')
document.write('<tr><td>Parola:</td><td><input type="password" name="parola" /></td></tr>')
document.write('<tr align="center"><td colspan=2><input type="submit" name="submit" value="Kaydet" /></td></tr></table>')
document.write('<INPUT TYPE="hidden" NAME="dil" VALUE="tr" /></form>')
}
</script> 
</body>