<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<body text="#ff0000" bgcolor="#000000" link="#ffffff" vlink="#999999" >
${_('anasayfalink')}
${_('formmenu')}
<table>
% for sonuc in c.sonuc:
        <tr><td width=100> </td><td>${sonuc}</td></tr>
% endfor
</table>
</body>