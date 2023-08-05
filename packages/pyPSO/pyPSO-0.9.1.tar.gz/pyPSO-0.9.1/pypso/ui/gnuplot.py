#-*- coding: utf-8 -*-
'''Modul rysujący wykres na bierząco.
'''
from Numeric import array, average
from Gnuplot import Gnuplot, Data

from pypso.ui import uiPsoAbstract

class uiPso(uiPsoAbstract):
    def step(self):
        i = self.old_step()        
        if i==1:
            self.uiinit()        
        if i % 10 == 0:
            fitness = array([ agent.get_fitness() for agent in self._pso._agents])
            speed = array([ agent.get_V() for agent in self._pso._agents])
            self.gbest.append(self._pso.get_gbest())
            self.worse.append(min(fitness))
            self.best.append(max(fitness))
            self.average.append(average(fitness))
            self.speed.append(average(speed))
        if i % 10 == 0:
            self._gnuplot.plot( Data(self.gbest, title="Global best"), Data(self.worse, title="Best"), Data(self.best, title="Worse"), Data(self.average, title="Average fittnes"), Data(self.speed, title="Speed"))            
        return i

    def uiinit(self):
        
        self.gbest = []
        self.best = []
        self.worse = []
        self.average = []
        self.speed = []
                
        self._gnuplot = Gnuplot()
        self._gnuplot.title('Zbieznosc algorytmu')        
        self._gnuplot('set data style linespoints')
        self._gnuplot('set logscale y')
        
