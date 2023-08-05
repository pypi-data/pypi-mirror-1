#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Wyświetla ui do służące do uruchamiania pso"""

import gobject
import gtk
#import threading

from pypso import library
from pypso import strategies
from pypso import functions
from pypso import pso
from pypso import ui
from pypso.widgets import PsoPainterClickable


class Parametr(gtk.HBox):    
    def __init__(self, name, parameter):        
        super(Parametr, self).__init__()
        label = gtk.Label(name)
        label.set_alignment(0,0.5)
        self.add(label)
        if(parameter.digits==0):
            step = 1
            page = 10
        else:
            step = (parameter.floatMax-parameter.floatMin)/100
            page = (parameter.floatMax-parameter.floatMin)/10
        adj = gtk.Adjustment(value=parameter.floatValue, lower=parameter.floatMin, upper=parameter.floatMax, step_incr=step, page_incr=page)
        adj.connect('value-changed', self.do_update)
        self._adj = adj
        self.add(gtk.SpinButton(adj, 1000, parameter.digits))        
        self.show_all()
        
        
    def do_update(self, adjusment):
        self.emit("changed", self.value)
        
    value = property(lambda self: self._adj.get_value(), doc="Aktualna wartość parametru")

gobject.signal_new("changed", Parametr, gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, (gobject.TYPE_FLOAT,))      

class Parametry(gtk.Frame):
    def __init__(self, opcje):
        opcje._parametry = self;
        super(Parametry, self).__init__(self)
        self.set_shadow_type(gtk.SHADOW_NONE)
        label = gtk.Label('<b>Parametry</b>')
        label.set_use_markup(True)
        self.set_label_widget(label)
        opcje._combo.connect('changed', self.do_combo_changed)
        self._box = gtk.VBox()
        self.add(self._box)
        self.model = {} 
        
    def do_combo_changed(self, combo):
        '''Przy zmianie combosa powinny zostać wyświetlone opcje'''        
        element = combo.get_model().get_value(combo.get_active_iter(),0)
        parameters = combo.library.get(element)[0].parameters()
        self.model = {} 
        
        for children in self._box:
            self._box.remove(children)
            del children
            
        for par in parameters:
            parametr = Parametr(par, parameters[par])
            parametr.parname = par
            parametr.connect("changed", self.do_parametr_changed)
            self.model[par] = parametr.value
            self._box.pack_start(parametr, False, False)
            
        self.emit('psochanged')
        
            
    def do_parametr_changed(self, parametr, value):
        self.model[parametr.parname] = value
        self.emit('psochanged')

gobject.signal_new("psochanged", Parametry, gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, ())

class Opcje(gtk.Frame):    
    def __init__(self, library):
        self.library = library;
        super(Opcje, self).__init__(self)
        self.set_shadow_type(gtk.SHADOW_OUT)
        box = gtk.VBox()
        self.add(box)

        self._label = gtk.Label()        
        self._label.set_use_markup(True)        
        self.set_label_widget(self._label)
        
                
        #Dodanie comboboxu do wybierania
        liststore = gtk.ListStore( gobject.TYPE_STRING, gobject.TYPE_STRING)
        combobox = gtk.ComboBox(liststore)
        
        cell = gtk.CellRendererText()
        combobox.pack_start(cell, False)
        combobox.add_attribute(cell, 'text', 0)
        
        self._lista = liststore
        self._combo = combobox
        combobox.library = library
        
        box.pack_start(combobox, False, False)
        self._combo.connect('changed', self.do_combo_changed)
        #szczegółowy opis
        self._text = gtk.Label()
        self._text.set_line_wrap(True)
        self._text.set_line_wrap_mode(gtk.WRAP_WORD)
        self._text.set_size_request(200,100)
        self._text.set_alignment(0,0)
        #self._text.set_width_request(200)
        box.pack_start(self._text, False)     
        params = Parametry(self)
        params.connect('psochanged', lambda x: self.emit('psochanged'))
        box.pack_start(params, False)
        self._wypelnij_opcje()
        
        #self.set_size_request(250,0)
        self.set_border_width(3)
        
    def do_combo_changed(self, combo):
        self._text.set_text(combo.get_model().get_value(combo.get_active_iter(),1))
        self._nazwa = combo.get_model().get_value(combo.get_active_iter(),0)
        
    
    def _wypelnij_opcje(self):    
        """Wypełnia listę opcji"""
        for tekst in self.library.get():
            self._lista.set(self._lista.append(), 0, tekst[1], 1, tekst[2])
            self._combo.set_active(0)

        
    def get_opcje(self):
        return {'parametry': self._parametry.model, 'nazwa': self._nazwa}

#gobject.signal_new("psochanged", Opcje, gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, ())

class OpcjeFunkcji(Opcje):
    def __init__(self):
        super(OpcjeFunkcji, self).__init__(library.function_library)
        self._label.set_label('<b>Funkcja</b>');
        
    
class OpcjeStrategii(Opcje):
    def __init__(self):
        super(OpcjeStrategii, self).__init__(library.strategy_library)
        self._label.set_label('<b>Strategia</b>');
        
        

class PaneleOpcji(gtk.VBox):
    def __init__(self):
        super(PaneleOpcji, self).__init__()
        self._of = OpcjeFunkcji()
        self._of.connect('psochanged', lambda x: self.emit('changed'))
        self.add(self._of)
        self._os = OpcjeStrategii()
        self._os.connect('psochanged', lambda x: self.emit('changed')) 
        self.add(self._os)
    def get_opcje(self):
        return {'strategia': self._os.get_opcje(),
                'funkcja': self._of.get_opcje()
                }

gobject.signal_new("changed", PaneleOpcji, gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, ())
        
class PanelKontrolny(gtk.Frame):
    def __init__(self, paneleOpcji):
        super(PanelKontrolny, self).__init__()
        self.set_shadow_type(gtk.SHADOW_OUT)
        
        label = gtk.Label("<b>Sterowanie</b>")
        label.set_use_markup(True)
        self.set_label_widget(label)
        box = gtk.VBox()
        self.add(box)
        
        paneleOpcji.connect('delete-event', self.do_destroy)
        #self.connect('delete-event', self.do_destroy)
        
        tb = gtk.Toolbar()
        box.pack_start(tb, False, False)
        
        self.pso_painter = PsoPainterClickable() 
        box.pack_start(self.pso_painter)  
             
        self._box = box

        run = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
        stop = gtk.ToolButton(gtk.STOCK_MEDIA_STOP)
        step = gtk.ToolButton(gtk.STOCK_MEDIA_NEXT)
        rewind = gtk.ToolButton(gtk.STOCK_MEDIA_REWIND)
        tb.insert(run, 0)
        tb.insert(step, 1)
        tb.insert(stop, 2)
        tb.insert(rewind, 3)
        run.connect("clicked", self.do_run)
        step.connect("clicked", lambda x: self.pso.step())
        stop.connect("clicked", self.do_stop)
        rewind.connect("clicked", self.do_restart )
                
        self.paneleOpcji = paneleOpcji
        paneleOpcji.connect('changed', self.set_pso_opcje)
        self._pso = False
   
    def do_restart(self, *args):
        self.do_stop()        
        self.set_pso_opcje()
        self.pso.restart()
        self.pso_painter.update()
             
    def set_pso_opcje(self, *args):
        opcje = self.paneleOpcji.get_opcje()
        f = functions.function_library.get(opcje['funkcja']['nazwa'])[0]
        s = strategies.strategy_library.get(opcje['strategia']['nazwa'])[0]
        for parametr in opcje['funkcja']['parametry']:
            f._parameters[parametr].floatValue = opcje['funkcja']['parametry'][parametr]
        for parametr in opcje['strategia']['parametry']:
            s._parameters[parametr].floatValue = opcje['strategia']['parametry'][parametr]            
            pass
        self.pso.set_function(f)
        self.pso.set_strategy(s)
        
         
    def get_pso(self):
        if self._pso == False:
            self._pso = pso.Pso()
            self.pso_painter.setModel(self._pso)
            self.set_pso_opcje()
        return self._pso
    pso = property(get_pso , doc="Pso")    
        
    def do_run(self, widget):
        #self.do_restart()
        self._loop = True;
        i = 0
        while self._loop:
            self.pso.step()
            i = i+1
            if(i%1000):
                gtk.main_iteration()
                
            

    def do_stop(self, *args):
        self._loop = False;

            
    def do_destroy(self, *args):
        self.do_stop()
        
        
class Window(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self) 
        self.set_size_request(800,600)
        self.connect('destroy', self.do_destroy)
        paneleGlowne = gtk.HPaned()
        po = PaneleOpcji()
        paneleGlowne.add(po)
        pk = PanelKontrolny(po)
        paneleGlowne.add(pk)
        
        self.add(paneleGlowne)
        self.connect('destroy', pk.do_destroy)
        
        self.show()
        self.show_all()
            
    def do_destroy(self, window):
        
        gtk.main_quit()
            
            
if __name__ == "__main__":
  #  gtk.gdk.threads_init()
    mw = Window()
    gtk.main()
