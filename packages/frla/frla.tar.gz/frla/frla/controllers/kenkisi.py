#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from frla.lib.base import *

import pg
from frla.lib import baglan
from pylons.i18n import get_lang, set_lang

log = logging.getLogger(__name__)

class KenkisiController(BaseController):

    def index(self):
	db=baglan.baglan()
	
	set_lang(g.lang)
	
	kisi="SELECT DISTINCT AcctStartTime from radacct where Username='"+request.params['isim']+"' and nasipaddress='"+request.params['ken']+"'"
	bilgiler=db.query(kisi)
	bilgiler=bilgiler.getresult()
	baglanmasayisi=db.query("SELECT COUNT(DISTINCT AcctStartTime) FROM radacct WHERE Username='"+request.params['isim']+"' and nasipaddress='"+request.params['ken']+"'")
	baglanmasayisi=baglanmasayisi.getresult()
	
	c.sonuc=[_('bilgikisi')+request.params['isim']+_('kenkisi')+request.params['ken']+_('kenbilgisi2')+ungettext('%(num)d time', '%(num)d times', int(baglanmasayisi[0][0])) % {'num': int(baglanmasayisi[0][0])}]
	tarih=0
	for i in bilgiler:
		if tarih==i[0][:i[0].find(' ')]:
			c.sonuc[len(c.sonuc):]=[g.bqac+_('saat')+i[0][i[0].find(' '):]+g.bqkapa]
		else:
			c.sonuc[len(c.sonuc):]=[_('tarih')+'</b>'+i[0][:i[0].find(' ')]+g.bqac+_('saat')+i[0][i[0].find(' '):]+g.bqkapa]
    		tarih=i[0][:i[0].find(' ')]
        
        return render('/sonuc2.mako')