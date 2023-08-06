#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import pg
from frla.lib import baglan

from pylons.i18n import get_lang, set_lang

from frla.lib.base import *

log = logging.getLogger(__name__)

class TarihController(BaseController):

    def index(self):
	db=baglan.baglan()
	tarihler=db.query("SELECT DISTINCT AcctStartTime from radacct")
	tarihler=tarihler.getresult()
	tarihler.reverse()
	
	g.lang=request.params['dil']
	set_lang(g.lang)
	
	c.sonuc=[_('tarih1')]
	tarihler[0]=tarihler[0][0][:tarihler[0][0].find(' ')]
	c.sonuc[len(c.sonuc):]=['<a href="/tarihbilgisi?tarih='+tarihler[0]+'">'+tarihler[0]+'</a><br>']
	for i in range(1,len(tarihler)-1):
		tarihler[i]=tarihler[i][0][:tarihler[i][0].find(' ')]
		if tarihler[i]==tarihler[i-1]:
			continue
    		c.sonuc[len(c.sonuc):]=['<a href="/tarihbilgisi?tarih='+tarihler[i]+'">'+tarihler[i]+'</a><br>']
        
        return render('/sonuc.mako')
