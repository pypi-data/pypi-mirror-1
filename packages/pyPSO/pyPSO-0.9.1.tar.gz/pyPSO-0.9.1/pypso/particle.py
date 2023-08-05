#-*- coding: utf-8 -*-
from pypso.functions import Boundary, Function, ELengthMismatch, Vector
from math import *

BIG_FLOAT = 9999999999999999999999999999999999.9

class Particle:
        '''
        Cząsteczka. Sama wylicza swoją fitness.    
        '''
        #TODO: dodać lazy fitnes.
        def __init__(self, pso):
                self._pso = pso
                self._p = Vector(boundary = pso.get_function().boundary)
                self._v = Vector([0 for i in pso.get_function().boundary])
                self._best = BIG_FLOAT
                self._bestpos = self._p[:]
                self.__fitness = None
        def get_fitness(self):
            if self.__fitness == None:                 
                self.__fitness = self._pso.get_function()(self._p)
                if self.__fitness<self._best:
                        self._best = self.__fitness 
                        self._bestpos = self._p[:]
            return self.__fitness
        
        fitness = property(get_fitness, doc="Wartość funkcji przystosowania")
            
                
        def get_V(self):   
            '''Długość wektora prędkości'''
            try:
               return sqrt(sum(map(lambda x: x**2,self._v)))
            except OverflowError, E:
               return 1.797e+308
        def get_best(self):
                '''Najlepsza wartość fitness'''
                return self._best
        def get_bestpos(self):
                '''Położenie w którym fitness było najlepsze'''
                return self._bestpos
        def __str__(self):
                return "p: %s\nv: %s\nfitness: %f" %(str(self._p), str(self._v), self.fitness)
        def step(self):
                '''Wykonanie kroku'''
                self._p = self._p + self._v
                self.__fitness = None
                self.boundaryCheck()
                
        def boundaryCheck(self):
                '''Obcięcie pozycji do dozwolonej wielkości świata'''
                try:
                        self._p = Vector(map(lambda x,b: min(max(x,b[0]), b[1]), self._p, self._pso.get_function().boundary))
                except:
                        raise ELengthMismatch
