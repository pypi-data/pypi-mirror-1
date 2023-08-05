#-*- coding: utf-8 -*-
'''Statystyki za pomocą gnuplota
Moduł dostarcza funkcję dekoruj_pso, która dekoruje obiekt pso umożliwiając tworzenie statystyk, oraz ostatecznie ich wyświetlenie.
'''
#from Gnuplot import Gnuplot, Data
from datetime import datetime
from Numeric import average, array

def decorate_pso(pso, wyswietlaj=False, wypisuj=True):
    '''Zwraca udekorowany obiekt pso obsługujący wykresy'''
    __plotPso(pso, wyswietlaj, wypisuj)
    return pso 

class __plotPso:
    '''Przechowuje wykresy, dekoruje pso'''
    def __init__(self, pso, wyswietlaj, wypisuj):                
        #Konfiguracja wykresiku
        self._pso = pso
        self._plot = []
        self._plotavg = []
        self._plotmax = []
        if wyswietlaj:
            self._gnuplot = Gnuplot()
            self._gnuplot.title('Zbierznosc algorytmu')        
            self._gnuplot('set data style linespoints')         
            self._gnuplotdata = Data('asd')
        self._t = datetime.now()
        self._wyswietlaj=wyswietlaj
        self._wypisuj=wypisuj
        #właściwe udekorowanie
        pso.__oldstep = pso.step        
        pso.step = self.step
        
        
    def _statystyka(self):
        pass
    def step(self):
        if self._wypisuj and self._pso._stepno==1:
            #print "Funkcja: %s" % self._pso.get_function().__doc__
            f = [f for f in self._pso.function_library.get() if f[0]==self._pso.get_function()][0]
            s = [s for s in self._pso.strategy_library.get() if s[0]==self._pso.get_strategy()][0]
            print "#Parametry pso: (%s)" % ",".join(["%s=%s" % (p,self._pso._parameters[p].value) for p in self._pso._parameters])
            print "#Funkcja: %s" % f[1]
            print "#\tParametry funkcji: (%s)" % ",".join(["%s=%s" % (p,f[0]._parameters[p].value) for p in f[0]._parameters])
            #print "#Strategie: %s" % ",".join([st[1] for st in s])
            
            print "#Strategia: %s" % s[1]
            print "#\tParametry strategii: (%s)" % ",".join(["%s=%s" % (p,s[0]._parameters[p].value) for p in s[0]._parameters])
            print "#step, g_best_fit, best_fit, worse_fit, avg_fit, avg_speed"
                
        self._pso.__oldstep()
        if self._pso._stepno % 10 == 0:
            self._plot.append((self._pso._stepno, self._pso.get_gbest()) )
            fitness = array([ agent.get_fitness() for agent in self._pso._agents])
            speed = array([ agent.get_V() for agent in self._pso._agents])
            #avg_speed = [agent.]
            if self._wyswietlaj:
                self._plotmax.append((self._pso._stepno, max(fitness)))
                self._plotavg.append((self._pso._stepno, average(fitness) ))
                self._gnuplot.plot(self._plot, self._plotavg, self._plotmax)            
            t = datetime.now()
            if self._wypisuj:
                #print self._pso._stepno, t - self._t, self._pso.get_gbest(), self._pso.get_gbestpos()
                print self._pso._stepno, self._pso.get_gbest(), min(fitness), max(fitness), average(fitness), average(speed)
            if self._wyswietlaj:	
                 self._gnuplot.itemlist.append((self._pso._stepno, self._pso.get_gbest()))
            self._t= t
        return self._pso._stepno

