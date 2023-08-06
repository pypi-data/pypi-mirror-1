#!/usr/bin/python
# -*- coding: utf-8 -*-
import pg
def baglan():
	db=pg.connect(dbname='firla',host='localhost',user='mehtap',passwd='')
	return db