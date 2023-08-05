#-*- coding: utf-8 -*-
'''Moduł zawiarający strategie poruszania się agentów'''
from random import random, choice
try:
    from Numeric import sqrt
except:
    from numpy import sqrt
from datetime import datetime

from pypso.library import strategy_library
from pypso.functions import Vector, Boundary
from pypso.parameters import Parameters
from pypso.particle import Particle


BIG_FLOAT = 9999999999999999999999999999999999.9

class Strategy(Parameters):
    """Nadklasa wszystkich strategii"""
    __parameters__ = {'m': (30, 5, 10000, 0, 'rozmiar stada') }
    def __init__(self):        
        super(Strategy, self).__init__()
    
    def __call__(self, pso):
        raise NotImplementedError("Strategia powinna nadpisywać metodę call")
    
    def restart(self, pso):
        '''Inicjuje pso tworząc losowe cząsteczki'''
        for i in range(int(self['m'])):
             pso._agents.append(Particle(pso))

class randomStrategy(Strategy):
    def __call__(self, pso):
        for agent in pso._agents:
            agent._v = Vector([(random()-0.5)/100 for i in agent._v ])
#strategy_library.register(randomStrategy(),'random','Dodanie losowej prędkości')

class randomStrategy2(Strategy):
    def __call__(self, pso):
        for agent in pso._agents:
            agent._v = Vector([v+(random()-0.5)/100 for v in agent._v ])
#strategy_library.register(randomStrategy(),'random2','Dodanie losowego przyśpieszenia')

randomv = lambda n: Vector([random() for i in range(n)])


class SelekcjaPojedyncza(Strategy):
    def __init__(self):
        super(SelekcjaPojedyncza, self).__init__()
        self.gb = None
        self.gb_value = BIG_FLOAT 
    
    def restart(self, pso):
        super(SelekcjaPojedyncza, self).restart(pso)
        self.gb = None
        self.gb_value = BIG_FLOAT
        
    def selekcja(self, agenci):
        value, agent = min([ (agent.fitness, agent) for agent in agenci])        
        if self.gb_value > value:
            self.gb = agent._p[:]
            self.gb_value = value
        return self.gb


class NSelekcja(Strategy):
    '''Pamiętane jest n najlepszych globalnych, i z tego wybierany jest losowo jeden'''
    def __init__(self):
        super(NSelekcja, self).__init__()
        self.ntab = None 
        self.gb = None

    def restart(self, pso):
        super(NSelekcja, self).restart(pso)
        self.gb = None
        self.ntab = None 

    def inicjuj(self, agenci, n):
        if not hasattr(self, 'ntab') or self.ntab==None:
            self.ntab = [ (agent.fitness, agent._p[:]) for agent in agenci]
            self.ntab.sort()
            self.ntab = self.ntab[:n]
    def selekcja(self, agent, i, pp):
        t = (agent.fitness, agent._p[:])
        if random()>pp:
            poz = choice(range(len(self.ntab)))
        else:
            poz = i % len(self.ntab)
        if(t[0]< self.ntab[poz][0]):
            self.ntab[i % len(self.ntab)] = t
            
        return self.ntab[poz][1]
        

 
class NleaderPso(NSelekcja):
    '''Pso z selekcją n liderami.'''
    
    def __init__(self):
        super(NSelekcja, self).__init__()
        parameters = (('c1', 2200,0, 10000, 3, 'wpływ lokalny'), 
                      ('c2', 2200,0, 10000, 3, 'wpływ globalny'),
                      ('w', 700,0, 10000, 3, 'bezwładność'),
                      ('n', 5,1, 10000, 0, 'liczba liderów'),
                      ('pp', 950,0, 1000, 3, 'prawdopodobieństwo wymiany informacji'))
        for par in parameters:
            self.add_parameter(*par)
        
    def __call__(self, pso):       
        self.inicjuj(pso._agents, int(self['n']))
        
        j = 0
        for agent in pso._agents:            
            b = agent.get_bestpos()
            j=j+1
            gb = self.selekcja(agent, j, self.parm('pp'))
           # print dir(self['pp'])            
            p = agent._p
            v = agent._v
            for i in range(len(v)):
                v[i] = self.parm('w') *(v[i] +self.parm('c1')*random()*(b[i]-p[i])+self.parm('c2')*random()*(gb[i]-p[i]))
 
class cleanPso(SelekcjaPojedyncza):
    '''Pso z uporzadkowanymi parametrami'''
    def __init__(self):
        super(cleanPso, self).__init__()
        parameters = (('zeta', 500,0, 1000, 3, 'wpływ własnej wiedzy'), 
                      ('xi', 810,0, 1000, 3, 'wpływ wiedzy'),
                      ('kappa', 3118,1500, 3500, 3, 'ścisk')  )
        for par in parameters:
            self.add_parameter(*par)
         
    def __call__(self, pso):        
        gb = self.selekcja(pso._agents)
        
        kappa = self.parm('kappa')
        xi = self.parm('xi')
        zeta = self.parm('zeta')
        for agent in pso._agents:
            b = agent.get_bestpos()            
            p = agent._p
            v = agent._v
            for i in range(len(v)):
                v[i] = (self.parm('kappa') )*((1-xi)*v[i] + xi*(zeta* random()*(b[i]-p[i])+(1-zeta)*random()*(gb[i]-p[i])))


class simplePso(SelekcjaPojedyncza):
    '''Proste pso'''
    def __init__(self):
        super(simplePso, self).__init__()
        parameters = (('c1', 2200,0, 10000, 3, 'wpływ lokalny'), 
                      ('c2', 2200,0, 10000, 3, 'wpływ globalny'),
                      ('w', 700,0, 10000, 3, 'bezwładność')  )
        for par in parameters:
            self.add_parameter(*par)
        
    def __call__(self, pso):        
        gb = self.selekcja(pso._agents)
        
        for agent in pso._agents:
            b = agent.get_bestpos()            
            p = agent._p
            v = agent._v
            for i in range(len(v)):
                v[i] = (self['w']/1000.0 )*(v[i] + self['c1']/1000.0*random()*(b[i]-p[i])+self['c2']/1000.0*random()*(gb[i]-p[i]))

class CFMPso(SelekcjaPojedyncza):
    '''Pso z Constriction Factor Method'''
    
    def __init__(self):
        super(CFMPso, self).__init__()
        parameters = (('c1', 2138,0, 4276, 3, 'wpływ lokalny'), 
                      ('c2', 2138,0, 4276, 3, 'wpływ globalny'),
                      ('k', 1000,577, 1000, 3, 'ścisk')  )
        for par in parameters:
            self.add_parameter(*par)
        
    def __call__(self, pso):
        gb = self.selekcja(pso._agents)
        fi = self.parm('c1')+self.parm('c2')
        if fi>4: 
            tfi = (2.0*self.parm('k'))/(fi - 2 + sqrt(fi**2-4*fi))
        else:
            tfi = 1
       # print tfi
        for agent in pso._agents:
			b = agent.get_bestpos()			
			p = agent._p
			v = agent._v
			for i in range(len(v)):
				v[i] = tfi*(v[i] + self.parm('c1')*random()*(b[i]-p[i])+self.parm('c2')*random()*(gb[i]-p[i]))            


class PSODE(SelekcjaPojedyncza):
    '''Pso ze ściskiem wyznaczanym różnicą'''
    
    def __init__(self):
        super(PSODE, self).__init__()
        parameters = (('c', 500,0, 1000, 3, 'wpływ lokalny'),) 
                   #   ('c2', 2200,0, 10000, 3, 'wpływ globalny'),)
               #       ('k', 700,0, 10000, 3)  )
        for par in parameters:
            self.add_parameter(*par)
        
    def __call__(self, pso):
        gb = self.selekcja(pso._agents)
       # fi = self.parm('c1')+self.parm('c2')
        #if fi>4: 
        #    tfi = 2.0/(fi - 2 + sqrt(fi**2-4*fi))
        #else:
        #    tfi = 1
        tfi = 1
        c = self.parm('c')
        for agent in pso._agents:
            b = agent.get_bestpos()            
            p = agent._p
            v = agent._v
            
            #v = (v + c*(b-p)+(1-c)*(gb-p))            
            dv = (choice(pso._agents)._p-choice(pso._agents)._p)
            #
            for i in range(len(v)):
                v[i] = dv[i]+(v[i] + c*(b[i]-p[i])+(1-c)*(gb[i]-p[i]))



strategy_library.register(simplePso(),'simple_PSO')
strategy_library.register(CFMPso(),'CFMPSO')
strategy_library.register(NleaderPso(),'Nleader')
strategy_library.register(PSODE(),'PsoDe')
strategy_library.register(cleanPso(),'cleanPso')


    
if __name__ == "__main__":
   print strategy_library.get()

