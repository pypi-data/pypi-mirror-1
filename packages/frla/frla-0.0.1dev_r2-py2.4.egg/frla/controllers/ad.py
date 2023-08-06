#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import pg
from frla.lib import baglan

from pylons.i18n import get_lang, set_lang

from frla.lib.base import *

log = logging.getLogger(__name__)

class AdController(BaseController):

    def index(self):
	db=baglan.baglan()
	adlar=db.query("SELECT DISTINCT UserName from radacct")
	adlar=adlar.getresult()
	adlar.sort()
	
	g.lang=request.params['dil']
	set_lang(g.lang)
	c.sonuc=[_('ad1')]
	for i in adlar:
		if i[0]=='anonymous@comu.edu.tr':
			continue
    		c.sonuc[len(c.sonuc):]=['<a href="/bilgikisi?ad='+i[0]+'">'+i[0][:i[0].find('@')]+'</a><br>']
        
        return render('/sonuc.mako')
