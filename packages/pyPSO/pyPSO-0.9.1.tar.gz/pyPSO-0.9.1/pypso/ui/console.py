#-*- coding: utf-8 -*-
'''Modul wypisujacy informacje o pso bezposrednio na konsoli, informacje te sa
bardzo przydatne dla gnuplota i innych aplikacji.
Domyslny sposob wyswietlania informacji o pso
'''
from Numeric import array, average

from pypso.ui import uiPsoAbstract

class uiPso(uiPsoAbstract):
	def step(self):
		i = self.old_step()		
		if i==1:
			self.uiinit()
		if i % 10 == 0:
			fitness = array([ agent.get_fitness() for agent in self._pso._agents])
			speed = array([ agent.get_V() for agent in self._pso._agents])
			print self._pso._stepno, self._pso.get_gbest(), min(fitness), max(fitness), average(fitness), average(speed)
		return i

	def uiinit(self):
		f = [f for f in self._pso.function_library.get() if f[0]==self._pso.get_function()][0]
		s = [s for s in self._pso.strategy_library.get() if s[0]==self._pso.get_strategy()][0]
		print "#Parametry pso: (%s)" % ",".join(["%s=%s" % (p,self._pso._parameters[p].value) for p in self._pso._parameters])
		print "#Funkcja: %s" % f[1]
		print "#\tParametry funkcji: (%s)" % ",".join(["%s=%s" % (p,f[0]._parameters[p].value) for p in f[0]._parameters])
		#print "#Strategie: %s" % ",".join([st[1] for st in s])
		
		print "#Strategia: %s" % s[1]
		print "#\tParametry strategii: (%s)" % ",".join(["%s=%s" % (p,s[0]._parameters[p].value) for p in s[0]._parameters])
		print "#step, g_best_fit, best_fit, worse_fit, avg_fit, avg_speed"
