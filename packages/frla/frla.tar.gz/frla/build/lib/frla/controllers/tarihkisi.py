#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from frla.lib.base import *

import pg
from frla.lib import baglan
from pylons.i18n import get_lang, set_lang

log = logging.getLogger(__name__)

class TarihkisiController(BaseController):

    def index(self):
	db=baglan.baglan()
	
	set_lang(g.lang)
	
	kisi="SELECT AcctStartTime,nasipaddress FROM radacct WHERE date_trunc('day',AcctStartTime)='"+request.params['tarih']+"'and Username='"+request.params['isim']+"'"

	bilgiler=db.query(kisi)
	bilgiler=bilgiler.getresult()
	sayi="SELECT COUNT(DISTINCT AcctStartTime) FROM radacct WHERE Username='"+request.params['isim']+"' and date_trunc('day',AcctStartTime)='"+request.params['tarih']+"'"

	baglanmasayisi=db.query(sayi)
	baglanmasayisi=baglanmasayisi.getresult()
	
	c.sonuc=[_('bilgikisi3')+request.params['tarih']+_('tarihbilgi2')+request.params['isim']+_('bilgikisi2')+ungettext('%(num)d time', '%(num)d times', int(baglanmasayisi[0][0])) % {'num': int(baglanmasayisi[0][0])}]
	saat=0
	for i in bilgiler:
		if saat==i[0][i[0].find(' '):]:
			continue
		ken_ad="SELECT ad FROM kenn WHERE adres='"+i[1]+"'"
		ken_ad=db.query(ken_ad)
		ken_ad=ken_ad.getresult()
		if len(ken_ad)==0:
			ken_ad=[(_('isimverme1')+i[1]+_('isimverme2'),)]
    		c.sonuc[len(c.sonuc):]=[_('saat')+i[0][i[0].find(' '):]+g.bqac+_('kenadres')+i[1]+_('ad')+ken_ad[0][0]+g.bqkapa]
		saat=i[0][i[0].find(' '):]
        
        return render('/sonuc2.mako')
