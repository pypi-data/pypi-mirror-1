#-*- coding: utf-8 -*-
'''Moduł zawierający optymalizowane funkcje'''
import random
from pypso.parameters import Parameters
try:
   from Numeric import *
except:
   from numpy import *
   Float = float64
class ELengthMismatch(Exception):
    '''Wyjątek podnoszony podczas niezgodności długości wektorów'''
    pass


#def gen_array(boundary):
	
	
def Vector(vector=[], boundary=None):
	if boundary == None:
		return array(vector, Float)
	generator = lambda i: random.random()*(boundary[i][1]-boundary[i][0])+ boundary[i][0]
	return array([generator(i) for i in range(len(boundary))], Float)


class Boundary:
    """
    Ograniczenia w przestrzeni. Losowanie wektora wymaga tego obietku aby mieć możliwość określenia przedziałów z których należy losować.
        Okraniczeniem jest zawsze para: (min,max)
    """
    def __init__(self, n, min=-5.2, max=5.2):
        "n -- liczba wymiarów"
        self.min = [ min for i in range(int(n))]
        self.max = [ max for i in range(int(n))]
    def __getitem__(self, key):        
        return (self.min[key],self.max[key])
    def __setitem__(self, key, value):
        if value[0]>=value[1]:
            raise AttributeError() # min, max
        self.min[key], self.max[key] = value        
    def __len__(self):
        return self.max.__len__()
        
class Function(Parameters):
    """
    Funkcja, można obliczyć wartość dla jakigoś wektora, jak i pamięta swoje położenie.
    """        
    __parameters__ = {'n': (20, 2, 100, 0, 'rozmiar funkcji') }
    def __init__(self, f, min=-5.2, max=5.2):        
        super(Function, self).__init__()
        boundary = Boundary(self['n'], min, max) #nadawie wartości domyślnej
        self.f = f
        self._boundary = boundary
        self._min = min
        self._max = max
        
    def __call__(self, vector):
        return self.f(vector)
    def parameter_set(self, name, value):        
        if name=='n':
            self._boundary = Boundary(self['n'], self._min, self._max)
        super(Function, self).parameter_set(name,value)
    
    boundary = property(lambda self: self._boundary, doc="Zakres funkcji")

class Rastrigin(Function):
    '''Funkcja rastyigina, parametryzowana'''
    def __init__(self):              
        super(Rastrigin, self).__init__(None, -5.12, 5.12)
        self.add_parameter('A', 10000, 0, 20000,3, 'długość aplitudy')
        self.add_parameter('w', 2000, 0, 4000,3, 'amplituda')

    def __call__(self, x):
		A = self.parm('A')
		n=len(x)
		omega = self.parm('w')*pi
		return A*n+sum([xi**2-A*cos(omega*xi) for xi in x ])


def elmul(v1, v2):
    '''
    Funkcja wykonująca mnożenie na wektorach, argument po argumentrze i tworząca nowy wektor.
    '''
    return Vector(map(lambda k,l: k*l, v1, v2))

def prod(v):
    '''
    Funkcja tworząca produkt v.
    '''
    result = 1
    for i in v:
        result*=i    
    return result

from library import function_library

def _rosenbrock(x):
	sum = 0.0
	for i in range(len(x)-1):
		sum = sum + 100*(x[i+1]-x[i]**2)**2+(1+x[i])**2
	return sum

def _dixpri(x):
	n = len(x)
	sum = (x[0]-1)**2
	for i in range(1,n):
		sum=(i+1)*(2*x[i]**2-x[i]-1)**2
	return sum
	

def _easom(x):
	return - prod(map(cos, x))* exp(-sum(map(lambda i: (i-pi)**2, x)))+1

def _ackley(x):
	n = len(x)
	return -20*exp(-0.2*sqrt(1.0/n*sum(map(lambda xi: xi**2,x))))-exp(1.0/n*sum(map(lambda xi: cos(2*pi*xi),x)))+20+e

def _grienwangk(x):
	return 1+sum(map(lambda xi: (xi**2)/4000.0,x))-prod([ cos(x[i]/sqrt(i+1)) for i in range(len(x))])

def _schewefel(x):
	return sum(map(lambda xi: -xi*sin(sqrt(abs(xi))),x))

def _hiperelips(x):
    return sum([i*x[i]**2 for i in range(len(x))])

def _hiperelipsobr(x):
    return sum([ sum([j*x[j]**2 for j in range(i)]) for i in range(len(x))])


class Schaffer(Function):
    '''Schaffera'''
    __parameters__ = {'n': (2, 2, 2, 0, 'rozmiar funkcji') }
    def __init__(self):              
        super(Schaffer, self).__init__(None, -400, 400)
        
class Schafferf6(Schaffer):        
    '''Schaffera F6'''
    def __call__(self, x):
        xx = x[0]**2+x[1]**2
        return .5+(sin(xx**.5)-.5)/(1+.001*xx)

class Schafferf7(Schaffer):
    '''Schaffera F7'''
    def __call__(self, x):
        xx = x[0]**2+x[1]**2
        return xx*(sin(50*(xx)**.1 )**2+1)

def _shubert(x):
    return prod(map(lambda xi: sum([j*cos((j+1)*xi+1) for j in range(1,7)] ) ,x)) 


class Michalewicz(Function):
    '''Schaffera'''
    #__parameters__ = {'m': (10000, 0, 25000, 3, '') }
    def __init__(self):              
        self.__parameters__['m'] = (10000, 0, 25000, 3, '') 
        super(Michalewicz, self).__init__(None, 0, pi)
        
    def __call__(self, x):
        m = self.parm('m')
        return -sum( [sin(x[i])*(sin(i*x[i])**(2*m)) for i in range(len(x))])

function_library.register(Function(lambda x:sum(x*x),-5.2,5.2),'F1','De Jong F1')
function_library.register(Function(_rosenbrock,-2.048, 2.048),'F2','De Jong F2')
function_library.register(Function(_hiperelips,-5.12, 5.12),'he','Hiper-elipsoidalna')
function_library.register(Function(_hiperelipsobr,-5.12, 5.12),'heo','Hiper-elipsoidalna obrócona')
function_library.register(Function(_easom,-100,100),'easom','Funkcja Easoma')
function_library.register(Function(_ackley,-32.768,32.768),'ackley','Ackley\'a')
function_library.register(Rastrigin(),'rastrigin', 'Rastrigina')
function_library.register(Function(_grienwangk,-32.768,32.768),'grienwangk','Grienwangka')
function_library.register(Schafferf6(),'schafferf6', 'Schaffera F6')
function_library.register(Schafferf7(),'schafferf7', 'Schaffera F7')
function_library.register(Function(_schewefel, -500, 500),'schewefel','Schewafela')
function_library.register(Function(_shubert,-10,10),'shubert','Shuberta')
function_library.register(Function(Michalewicz(),-10,10),'michalewicz','Michalewicza')
#function_library.register(Function(_dixpri,-10,10),'dixpri','Funkcja Dixona i Price\'a')


if __name__ == "__main__":
    print sum([1,3,3,4])
    print prod([1,2,3,4,5,6])
    print elmul(Vector([1.,2]), Vector([2,0.5]))
    print Vector([1,3])+Vector([2,-4])
    f=function_library.get()[0][0]
    print f
    f['n']=4
    
