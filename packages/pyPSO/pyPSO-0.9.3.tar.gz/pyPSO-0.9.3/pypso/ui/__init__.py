#-*- coding: utf-8 -*-
'''Ui do gnuplota, standardowo jest tylko wyjście na zewnątrz za pomocą
treści'''

import sys


def decorate_pso(pso, nazwa):
	'''Zwraca udekorowany obiekt pso obsługujący wykresy, nazwa jest nazwą
	modułu zawierającą funkcje dekorującą pso o nazwia uiPso.'''
	try:
		modul = __import__('pypso/ui/%s' % nazwa)
		decorated = modul.uiPso(pso)
		if hasattr(decorated, '_initialize'):
			decorated._initialize()
	except ImportError, E:
		print >> sys.stderr,  "Błąd importu, brak modułu o nazwie %s" % nazwa
	return pso

class uiPsoAbstract:
	def __init__(self, pso):
		self._pso = pso
		self.old_step = pso.step
		pso.step=self.step
	def step(self):
		i = self.old_step()		
		return i
