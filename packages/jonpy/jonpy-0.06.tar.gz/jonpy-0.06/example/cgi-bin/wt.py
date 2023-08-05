#!/usr/local/bin/python

# $Id: wt.py,v 1.1 2002/05/02 00:11:56 jribbens Exp $

import jon.wt as wt
import jon.fcgi as fcgi


fcgi.Server({fcgi.FCGI_RESPONDER: wt.Handler}).run()
