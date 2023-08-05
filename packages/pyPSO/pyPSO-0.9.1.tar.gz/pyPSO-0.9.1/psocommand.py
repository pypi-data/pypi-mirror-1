#!/usr/bin/python
#-*- coding: utf-8 -*-
'''Moduł odpowiedzialny za uruchamianie algorytmu'''
from os import mkdir
from sys import argv
from pypso import pso
from pypso import ui
import re, sys
from datetime import datetime

def _wypisz_dostepne_funkcje(pso):
    l = ["Dostępne funkcje:\n"]    
    for f in pso.function_library.get():
        l.append("\t%s -- %s\n" % (f[1],f[2]))
    sys.stderr.writelines(l)


def _wypisz_dostepne_strategie(pso):
    l = ["Dostępne strategie:\n"]
    for f in pso.strategy_library.get():
        l.append("\t%s -- %s\n" % (f[1],f[2]))
    sys.stderr.writelines(l)



def _ustaw_strategie(pso, par):
    strategie = {}
    for s in pso.strategy_library.get():
        strategie[s[1]]=s[0]
    try:
        if par in strategie:
            pso.set_strategy(strategie[par])
        else:
            raise IndexError, "Nie istniejąca strategia %s" % par
    except IndexError, E:
        print E
        _wypisz_dostepne_strategie(pso)
        return False
    return True

def _ustaw_funkcje(pso, par):
    funkcje = {}
    for f in pso.function_library.get():
        funkcje[f[1]]=f[0]
    try:
        if par in funkcje:
            pso.set_function(funkcje[par])
        else:
            raise IndexError, "Nie istniejąca funkcja %s" % par
    except IndexError, E:
        print E
        _wypisz_dostepne_funkcje(pso)
        return False
    return True

def _ustaw_strategie(pso, par):
    strategie = {}
    for s in pso.strategy_library.get():
        strategie[s[1]]=s[0]
    try:
        if par in strategie:
            pso.set_strategy(strategie[par])
        else:
            raise IndexError, "Nie istniejąca strategia %s" % par
    except IndexError, E:
        print E
        _wypisz_dostepne_strategie(pso)
        return False
    return True

def _wyswietl_par_pso(pso):
    """Wyswietla parametry pso"""
    print "Dostępne parametry pso: " # ",".join(pso.get_function()._parameters.keys())
    pars =  pso._parameters
    for par in pars:
        print "\t%s - %s" % (par,pars[par].__doc__)
    return False

def _wyswietl_par_funkcji(pso):
    """Wyswietla parametry funkcji"""
    print "Dostępne parametry funkcji: " # ",".join(pso.get_function()._parameters.keys())
    pars =  pso.get_function()._parameters
    for par in pars:
        print "\t%s - %s" % (par,pars[par].__doc__)
    return False

def _wyswietl_par_strategii(pso):
    """Wyswietla parametry strategii"""
    print "Dostępne parametry strategii: " # ",".join(pso.get_function()._parameters.keys())
    pars =  pso.get_strategy()._parameters
    for par in pars:
        print "\t%s - %s" % (par,pars[par].__doc__)
    return False

def _ustaw_par_f(pso, nazwa, par):    
    '''Ustawia parametr nazwa funkcji na wartosc par'''
    try:
        pso.get_function()[nazwa]=int(par)
    except KeyError, E:
        print "Nieznany parametr funkcji %s" % E
        return _wyswietl_par_funkcji(pso)
    except ValueError, E:
        print "Parametr funkcji powinien być liczbą"
        return False
    return True

def _ustaw_par_str(pso, nazwa, par):    
    '''Ustawia parametr nazwa strategii o podanym numesze na wartosc par'''
    try:
        pso.get_strategy()[nazwa]=int(par)
    except KeyError, E:
        print "Nieznany parametr strategii %s" % (E,)
        return _wyswietl_par_strategii(pso)
        return False
    except ValueError, E:
        print "Parametr strategii powinien być liczbą"
        return False
    return True

def _ustaw_par_pso(pso, nazwa, par):    
    try:
        pso[nazwa]=int(par)
    except KeyError, E:
        print "Nieznany parametr pso %s" % (E,)
        return _wyswietl_par_pso(pso)
        return False
    except ValueError, E:
        print "Parametr pso powinien być liczbą"
        return False
    return True


def _usage(pso):
    print """Sposób użycia:
    psocommand [archiwizuj] [ui=typ_ui] [f=Nazwa funkcji] [f_parametr=wartość parametru funkcji] [s_parametr=wartość parametru strategii] [pso_parametr=wartość parametru pso]

    Gdzie:
        ui: ustawia sposób prezentacji wyników, można użyć wielokrotnie.
        archwizuj: spowoduje nie wyświetlanie wyników działania algorytmu na strdout, lecz zapisywanie go w katalogu doswiadczenia
        Informacje o dostępnych funkcjach, ui, strategiach mozna uzyskać wpisując ,,pomoc'' zamiast nazwy.
    """
    return False


def _wybierz_ui(pso, nazwa):
    zamieniacz = re.compile('^(?P<nazwa>[^\.]+).py$')
    from os import listdir
    if nazwa!='pomoc':
	      ui.decorate_pso(pso, nazwa)
	      return True
    else:
        print ui
        lista_ui = [ zamieniacz.match(plik).groupdict()['nazwa'] for plik in listdir('pypso/ui') if zamieniacz.match(plik)]
        lista_ui.remove('__init__')
        print '''Dostępne ui: 
            %s''' % ', '.join(lista_ui)
        return False

PARAMETRY=[
           (re.compile("^f=(?P<par>.*)"), _ustaw_funkcje),
           (re.compile("^s=(?P<par>.*)"), _ustaw_strategie),
           (re.compile("^f_(?P<nazwa>[^=]+)=(?P<par>.*)"), _ustaw_par_f),           
           (re.compile("^f_pomoc"), _wyswietl_par_funkcji),
           (re.compile("^pso_(?P<nazwa>[^=]+)=(?P<par>.*)"), _ustaw_par_pso),
           (re.compile("^pso_pomoc"), _wyswietl_par_pso),                      
           (re.compile("^s_(?P<nazwa>[^=]+)=(?P<par>.*)"), _ustaw_par_str),
           (re.compile("^s_pomoc"), _wyswietl_par_strategii),                                 
           (re.compile("^pomoc$"), _usage),
           (re.compile("^h$"), _usage),
           (re.compile("^h$"), _usage),
           (re.compile("^-h$"), _usage),
           (re.compile("^--help$"), _usage),
		   (re.compile("^ui=(?P<nazwa>[^=]+)$"), _wybierz_ui)
           ]

def run_pso():
    '''Pso inicjowane za pomocą parametrów'''    
   
    if 'archiwizuj' in argv[1:]:
        try:
           mkdir('doswiadczenia')
        except:
           pass
        sys.stdout = open("doswiadczenia/%s.dat" % datetime.today().strftime('%F-%T'),"w")
        argv.remove('archiwizuj')
    
    p = pso.Pso()
    if len(argv)==1:
        _usage(pso)
        exit()
    for arg in argv[1:]:
        for par,f in PARAMETRY:
            w=par.match(arg)
            if w:
                if not f(p,**w.groupdict()):
                    return
    p.restart()
    max_iterations = p['maxiter']
    while p.step()<max_iterations:
        pass


if __name__ == "__main__":
	run_pso()
