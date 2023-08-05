#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
Przetworzenie plików wejściowych i pogrupowanie uwzględniając podane parametry.
'''
import os, re
import Numeric



def opcje_doswiadczenia(tab, line=-1):
	'''Zwraca opcje doswiadczenia odczytane z tab, ktore to jest tablica linii
	pliku wyniku działania doświaczenia'''
	try:
			t=tab[:5]
			pso = parsuj_linie(t[0])
			func = parsuj_linie(t[2])
			stra = parsuj_linie(t[4])
			dict={'pso': parsuj_par(pso), 'f': parsuj_par(func), 's': parsuj_par(stra)}
			dict2={}
			for key in dict:
				for para in dict[key]:
					dict2['%s_%s' %(key,para[0])]=para[1]	
			wyn = tab[line][:-1].split(' ')
			dict2['step']=wyn[0]
			dict2['g_best_fit']=wyn[1]
			dict2['best_fit']=wyn[2]
			dict2['worse_fit']=wyn[3]
			dict2['avg_fit']=wyn[4]
			dict2['avg_speed']=wyn[5]
			dict2['f']=get_nazwa(tab[1])
			dict2['s']=get_nazwa(tab[3])
			return dict2
	except:
		return None


def wszystkie_doswiadczenia(kat, line=-1):
		'''Pobiera wsztstkie doświadczenia z wybranego katalogu
		'''
		try:
				m = re.compile(r'.*\.dat')
				dane = [opcje_doswiadczenia(file('%s/%s' % (kat,plik)).readlines(), line ) for plik in os.listdir(kat) if m.match(plik)]				
				
				dane = [dana for dana in dane if dana!=None]
				return dane
		except OSError, E:
			print "Pierwszym parametrem powinien być katalog ze statystykami."
			return []


def wypisz_dane(dane):
	'''Wypisuje dane na stdout'''
	stara_dana = ''
	for dana in dane: 
		if dana[0]!=stara_dana:
			print ''
			stara_dana=dana[0]
		print ' '.join(map(str, dana))


parametr_filtr=re.compile(r'^(?P<func>[^=\+-]+)(?P<rel>[=\+-])(?P<war>.*)$')
funkcja_filtrujace = {
		'-': lambda dos, filtr: float(dos[filtr['func']])<float(filtr['war']),
		'+': lambda dos, filtr: float(dos[filtr['func']])>float(filtr['war']),
		'=': lambda dos, filtr: str(dos[filtr['func']])==str(filtr['war'])
	}

def filtruj(doswiadczenia, filtry):
	'''Filtruje dane za pomocą filtrów'''
	wyn = doswiadczenia
	try:
		for filtr in filtry:
			wyn =  [dos for dos in wyn if funkcja_filtrujace[filtr['rel']](dos, filtr)]
		return wyn
	except KeyError, K:
		print "Nieznana kolumna %s, dostępne kolumny: %s" % (K, ', '.join(doswiadczenia[0].keys() ))
		return []


def _quantyl(jaki):
	def func(x):
		x.sort()
		return x[int(len(x)*jaki)]
	return func

def _stddev(x):
	sr = Numeric.average(x)
	return (Numeric.sum(map(lambda xi: (xi-sr)**2, x))/len(x))**.5

funkcje_srednie = {
		'avg': Numeric.average,
		'med': _quantyl(.5),
		'q1': _quantyl(.25),
		'q3': _quantyl(.75),
		'max': max,
		'min': min,
		'stddev': _stddev,
		
	}
def _grupuj(dane, kolumny, srednie, fsrednie):
	try:
			wynik = {}
			for dana in dane:
				desk = []
				wyn = []
				for k in kolumny:
					try:
						desk.append(float(dana[k]))
					except ValueError, E:
						desk.append(dana[k])
				for w in srednie:
					wyn.append(dana[w])
				wyn = Numeric.array(map(float,wyn))
				desk = tuple(desk)
				if wynik.has_key(desk):
					wynik[desk].append(wyn)
				else:
					wynik[desk]=[wyn]
			wynik2=[]
			
			for klucz in wynik:
				wiersz = [el for el in klucz]
				l = len(wynik[klucz])
				if l>0:
					for i in range(len(wynik[klucz][0])):
						try:
							myfunc = funkcje_srednie[fsrednie[i]]
						except KeyError, K:
							print "Nieznana funkcja statystyczna %s, dostępne funkcje: \n\t%s" % (K, "\n\t".join(funkcje_srednie.keys()))
							return []
						wiersz.append(myfunc(map(lambda x: x[i], wynik[klucz])))
					wynik2.append(wiersz)
			wynik2.sort()
			return wynik2
	except KeyError, K:
		print "Nieznana kolumna %s, dostępne kolumny: %s" % (K, ', '.join(dane[0].keys() ))
		return []

def tworz_statystyke(katalog, kolumny, filtry=None, srednie=None, linia=-1 , fsrednie=None):
	'''Tworzy statystyki dla podanego katalogu z danymi i przy użyciu podanych parametrów'''
	if srednie==None:
		srednie=[]
	if fsrednie==None:
		fsrednie=[]
	doswiadczenia = wszystkie_doswiadczenia(katalog, linia)
	if filtry!=None:
		doswiadczenia = filtruj(doswiadczenia, filtry)
	doswiadczenia = _grupuj(doswiadczenia, kolumny, srednie, fsrednie)	
	return doswiadczenia

def _wywal_uzyte(tab1, tab2):
	for i in range(len(tab1)):
		if tab2[i]!=None:
			tab1[i]=None

def _parsuj_srednie(tekst):
	if tekst:
		tekst = tekst.split('@')
		if len(tekst)==2:
			return tekst
	return None
	

def wypisz_dane(dane):
    '''Wypisuje dane na stdout'''
    stara_dana = ''
    print "# %s" % ' '.join(argv[2:])
    for dana in dane:
        if dana[0]!=stara_dana:
            print ''
            stara_dana=dana[0]
        print ' '.join(map(str, dana))


par=re.compile(r'.*\((?P<p>[^\)]+)\).*')
parsuj_linie = lambda linia: par.match(linia.split(':')[1]).groupdict()['p']
parsuj_par = lambda param: map(lambda x: x.split('='), param.split(','))
get_nazwa = lambda linia: linia.split(':')[1].strip()
numer_linii = re.compile(r'^iteracja=(?P<numer>[\-0-9]+)$')

def _nielinia(str):
	'''Zwraca str jeżeli nie jest parametrem od linii, '' jeżeli jest param od
	linii'''
	if not numer_linii.match(str):
		return str
	return ''

def _usage(katalog=None):
	"""Wypisuje sposób użycia"""
	print """Sposób użycia: 
	./dane.py katalog_z_danymi [iteracja=numer_iteracji] <filtry> <kolumny> <srednie>
	
numer_iteracji -- musi być podzielny przez 10
<filtry> -- wyrażenia postaci <kolumna><operator>wartosc, gdzie:
	<kolumna> nazwa kolumny,
	<operator> -- jeden ze znaków:
		,,='' -- pod uwagę będą brane tylko doświadczenia, w których kolumna miała dokładną wartość
		,,+'' -- pod uwagę będą brane tylko doświadczenia, w których kolumna miała większą wartość
		,,-'' -- pod uwagę będą brane tylko doświadczenia, w których kolumna miała mniejszą wartość
<kolumny> lista nazw kolumn, z których będą pobierane wartości do raportu
<srednie> lista nazw kolumn, poprzedzona znakiem @, z których wartości będą uśredniane w raporcie

W przypadku niepodania iteracji brana jest pod uwagę zawsze ostatnie iteracja, niezależnie od tego ile iteracji trwało doświadczenie.
"""
	if katalog!=None:
		doswiadczenia = wszystkie_doswiadczenia(katalog, -1)
		print "Dla katalogu %s dostępne są kolumny: \n\t%s" % (katalog, "\n\t".join(doswiadczenia[0].keys() ))
	exit()

if __name__ == '__main__':
	from sys import argv
	if len(argv)==1:
		_usage()
	kolumny= argv[2:]
	if len(kolumny)==0:
		_usage(argv[1])
	
	filtry=[parametr_filtr.match(_nielinia(arg)) for arg in kolumny ]	
	linie = [ numer_linii.match(arg) for arg in kolumny ]
	_wywal_uzyte(kolumny, filtry)
	srednie=map(_parsuj_srednie, kolumny)
	_wywal_uzyte(kolumny, srednie)
	_wywal_uzyte(kolumny, linie)
	
	linie = [linia.groupdict() for linia in linie if linia]
	try:
		linia= int(linie[0]['numer'])/10+5
	except:
		linia=-1
	
	filtry=[ filtr.groupdict() for filtr in filtry if filtr]
	kolumny=[ kolumna for kolumna in kolumny if kolumna]
	
	nowesrednie=[ srednia[1] for srednia in srednie if srednia]
	fsrednie=[ srednia[0] for srednia in srednie if srednia]
		
	if len(kolumny)+len(srednie)==0:
		print "Nie podałeś kolumn"
		_usage(argv[1])
	
	stat = tworz_statystyke(argv[1], 
			kolumny, 
			filtry=filtry, 
			srednie=nowesrednie,
			fsrednie=fsrednie,
			linia=linia)
	wypisz_dane(stat)


	