#!/usr/bin/env python

component_root = [
	{'components':'./components'},
	{'content':'./content'},
]
doccomp = ['document_base.myt']
output ='./html'

import sys,re,os.path
sys.path = ['../lib/', './lib/'] + sys.path

import documentgen

documentgen.genall(doccomp, component_root, output)



