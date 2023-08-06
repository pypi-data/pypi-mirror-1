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
${g.homepage}
<br>
<script type="text/javascript">
if (secenek==0){
document.write('<h3><font color="ff0000">Configuration of Network Attached Storage Name</font></h3><br>')
document.write('<form name="ekle" method="POST" action="/nasconf/ekleme">')
document.write('Address: <input type="text" name="adres" value="'+adres+'"> ')
document.write('Name: <input type="text" name="isim" /> ')
document.write('<input type="submit" name="ekle" value="   Add   " /></form>')

if (adres==""){ 
document.write('<form name="degistir" method="POST" action="/nasconf/degistirme">Address: <input type="text" name="adres" /> Name: <input type="text"name="isim" /> <input type="submit" name="degistir" value="Modify" /></form>')
document.write('<form name="sil" method="POST" action="/nasconf/silme">Address: <input type="text" name="adres" /> Name: <input type="text" name="isim" /> <input type="submit" name="sil" value="Delete" /></form>')
document.write("*For deleting, it's enough to fill only one field.<br>")
} 
document.write('<br><form name="listele" method="POST" action="/nasconf/listele">')
document.write('Listing: <input type="submit" name="listele" value="List" /></form>')
}
else if (secenek==1){
document.write('<h3><font color="ff0000">Database Connection Setup</font></h3><br>')
document.write('<form name="dbdeger" method="POST" action="/dbayar/ayarla">')
document.write('<table><tr><td>Database Name:</td><td><input type="text" name="vtisim" /></td></tr>')
document.write('<tr><td>Host:</td><td><input type="text" name="host" /></td></tr>')
document.write('<tr><td>User:</td><td><input type="text" name="kullanici" /></td></td>')
document.write('<tr><td>Password:</td><td><input type="password" name="parola" /></td></tr>')
document.write('<tr align="center"><td colspan=2><input type="submit" name="submit" value="Save" /></td></tr></table>')
document.write('<INPUT TYPE="hidden" NAME="dil" VALUE="en"></form>')
}
</script>
</body> 
