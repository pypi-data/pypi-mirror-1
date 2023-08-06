#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from frla.lib.base import *
import pg
from frla.lib import baglan
from pylons.i18n import get_lang, set_lang

log = logging.getLogger(__name__)

class KenyapilandirmaController(BaseController):
    
    def form(self):
	    return render('/form.mako')
    def ekleme(self):
	db=baglan.baglan()
	
	g.lang='tr'
	set_lang('tr')
	try:
		if request.params['adres'].strip()!="" and request.params['isim'].strip()!="":
			ekle="INSERT INTO kenn VALUES('"+request.params['adres']+"', '"+request.params['isim']+"')"
			db.query(ekle)
        		c.sonuc=[_('ekleme1')]
			return render('/sonuc2.mako')
		else:
			c.sonuc=[_('ekleme2')]
			return render('/sonuc2.mako')
	except:
		try:
			tablo_olusturma="CREATE TABLE kenn(adres CHAR(20) PRIMARY KEY NOT NULL, ad CHAR(30))"
			db.query(tablo_olusturma)
			if request.params['adres'].strip()!="" and request.params['isim'].strip()!="":
				ekle="INSERT INTO kenn VALUES('"+request.params['adres']+"', '"+request.params['isim']+"')"
				db.query(ekle)
        			c.sonuc=[_('ekleme1')]
				return render('/sonuc2.mako')
			else:
				c.sonuc=[_('ekleme2')]
				return render('/sonuc2.mako')
		except:
			c.sonuc=[_('ekleme2')]
			return render('/sonuc2.mako')
	
    def degistirme(self):
	db=baglan.baglan()
	
	g.lang='tr'
	set_lang('tr')
	try:
		if request.params['adres'].strip()!="" and request.params['isim'].strip()!="":
			degistir="UPDATE kenn SET adres='"+request.params['adres']+"', ad='"+request.params['isim']+"' WHERE adres='"+request.params['adres']+"'"
			db.query(degistir)
			c.sonuc=[_('degistirme1')]
			return render('/sonuc2.mako')
		else:
			0/0
	except:
		c.sonuc=[_('degistirme2')]
		return render('/sonuc2.mako')
	
    
    def silme(self):
	db=baglan.baglan()
	
	g.lang='tr'
	set_lang('tr')
	try:
		if request.params['adres'].strip()=="" and request.params['isim'].strip()=="":
			mesaj=[_('silme2')]
		elif request.params['adres'].strip()=="" and request.params['isim'].strip()!="":
			sil="DELETE FROM kenn WHERE ad='"+request.params['isim']+"'"
			db.query(sil)
			mesaj=[_('silmead')]
		elif request.params['isim'].strip()=="" and request.params['adres'].strip()!="":
			sil="DELETE FROM kenn WHERE adres='"+request.params['adres']+"'"
			db.query(sil)
			mesaj=[_('silmeadres')]
		else:
			sil="DELETE FROM kenn WHERE adres='"+request.params['adres']+"' AND ad='"+request.params['isim']+"'"
			db.query(sil)
			mesaj=[_('silme1')]
		
	except:
		c.sonuc=[_('silme2')]
		return render('/sonuc2.mako')
	c.sonuc=mesaj
	return render('/sonuc2.mako')

    def listele(self):
	db=baglan.baglan()
	
	g.lang='tr'
	set_lang('tr')
	try:
		listele="SELECT * FROM kenn"
		tablo=db.query(listele)
		tablo=tablo.getresult()
		liste='<table><tr><td>'+_('listele1')+'</td><td>'+_('listele2')+'</td></tr>'
		for i in tablo:
			liste=liste+'<tr><td>'+i[0]+'.....</td><td>'+i[1]+'</td></tr>'
		liste=liste+'</table>'
		c.sonuc=[liste]
		return render('/sonuc2.mako')
	except:
		c.sonuc=[_('liste')]
		return render('/sonuc2.mako')