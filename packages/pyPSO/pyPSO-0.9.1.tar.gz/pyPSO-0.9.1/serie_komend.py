#!/usr/bin/python
#-*- coding: utf-8 -*-
'''Wykonuje serie komend, parametry w linii poleceń w postaci [start:stop:step]
rozwijane są na sekwencje poleceń'''

def rozwin(komendy):
	l = len(komendy[0])
	for j in range(l):
		nowe = []
		for komenda in komendy:
			m = seria.match(komenda[j])
			if m:
				dict = m.groupdict()
				steps=map(float,dict['dane'].split(':'))
				i=steps[0]
				while(i<=steps[1]):
					komenda[j]=dict['poczatek']+str(int(i))
					nowe.append(komenda[:])
					i=i+steps[2]
			else:
				nowe.append(komenda[:])
		komendy=nowe[:]
	return komendy

from sys import argv
import re
seria=re.compile('^(?P<poczatek>[^\[]*)\[(?P<dane>.+)\]$')

import os
komendy = rozwin([argv[1:]])
l = len(komendy)
i=1
for komenda in komendy:
	k = ' '.join(komenda)
	print "Wykonuje: ,,%s'' (%s/%s)" % (k, i, l)
	i=i+1
	os.system(k)

