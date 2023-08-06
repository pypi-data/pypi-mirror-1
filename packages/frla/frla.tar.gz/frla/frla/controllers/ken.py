#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import pg
from frla.lib import baglan

from pylons.i18n import get_lang, set_lang

from frla.lib.base import *

log = logging.getLogger(__name__)

class KenController(BaseController):

    def index(self):
	db=baglan.baglan()
	kenler=db.query("SELECT DISTINCT nasipaddress from radacct")
	kenler=kenler.getresult()
	
	g.lang=request.params['dil']
	set_lang(g.lang)
	
	c.sonuc=[_('kenler')]
	c.sonuc[len(c.sonuc):]=['<table>']
	for i in kenler:
		ken_ad="SELECT ad FROM kenn WHERE adres='"+i[0]+"'"
		ken_ad=db.query(ken_ad)
		ken_ad=ken_ad.getresult()
		if len(ken_ad)==0:
			ken_ad=[(_('isimverme1')+i[0]+_('isimverme2'),)]
    		c.sonuc[len(c.sonuc):]=['<tr><td><a href="/kenbilgisi?ken='+i[0]+'">'+i[0]+'</a></td><td>'+ken_ad[0][0]+'<br></td></tr>']
	c.sonuc[len(c.sonuc):]=['</table>']	
        
        return render('/sonuc.mako')
