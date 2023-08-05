#-*- coding: utf-8 -*-
'''Wyświetlanie ruch cząsteczek w okienu gtk
'''
from Numeric import array, average
import pygtk; pygtk.require("2.0")
import gtk
from gtk import gdk, glade
import gobject
import threading, thread

from pypso.widgets import PsoPainter
from pypso.ui import uiPsoAbstract

class Window(gtk.Window):
    """Okienko służące do wyświetlania podgłądu stada"""
    def __init__(self,pso):
        gtk.Window.__init__(self)
        self.set_title('PSO, podgląd stada')
        self.set_default_size(700, 700)
        self.pso_painter = PsoPainter()
        self.pso_painter.setModel(pso)
        self.add(self.pso_painter)
        self.show_all()
        
	 

class uiPso(uiPsoAbstract):
    """Element ui, umożliwiający wyświetlanie stada w okienku rzutującym położenie osobników na płąszczyznę."""
    def _initialize(self):
        gtk.gdk.threads_init()
        mw = Window(self._pso)
        self._pso._gtkwidget = mw.pso_painter
        thread.start_new_thread(gtk.main, ())
        
        
	def step(self):
		i = self.old_step()		
		return i


