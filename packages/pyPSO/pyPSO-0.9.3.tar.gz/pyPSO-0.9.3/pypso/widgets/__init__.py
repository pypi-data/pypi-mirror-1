#-*- coding: utf-8 -*-

import gtk, gobject
from gtk import gdk

class PsoPainterClickable(gtk.EventBox):
    def __init__(self):
        super(PsoPainterClickable, self).__init__()
        
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.do_button_press)
        self._painter = PsoPainter()
        self.add(self._painter)
        
    def setModel(self, model):
        self._painter.setModel(model)
    def update(self):
        self._painter.updateScalers()
        self._painter.update()

    def do_button_press(self, widget, event):
        self._painter.do_click(event)
    

class PsoPainter(gtk.DrawingArea):
    '''Widget gtk rysujący pso za pomocą rzutu wszystkich obiektów na płaszczyznę R**2'''
    def __init__(self):        
        super(PsoPainter, self).__init__()        
        self.connect('configure_event', self.do_configure)
        self.connect('realize', self.do_realize)
        self.connect('expose_event', self.do_expose)
        
        #self.connect('event', self.do_button_press)
        self.show()
        self._cairo = None
        self.model = None
        self._window2dboundary = None
        self._scalers = (1,1)     
        self.update()
        #Uaktualniaj 5/s           
        gobject.timeout_add(1000/5, self.update)
        

    
    def do_configure(self, painter, event):   
        self._window2dboundary = [0,0, painter.window.get_geometry()[2], painter.window.get_geometry()[3]]
        if self.model:
            self.updateScalers()
        return False
                   
        
    def do_realize(self, painter):        
        return False
        
    def do_click(self, event):
        #print event, event.button, event.x, event.y
        if hasattr(self, '_selected'):
            del self._selected._is_selected
        if(hasattr(self.model,'_agents')):
            pos = lambda agent, n: (agent._p[n]-self.getFunc2DBoundary()[n][0])*self._scalers[n]
            min = [ ( (pos(agent,0)-event.x)**2 + (pos(agent,1)-event.y)**2, agent) for agent in self.model._agents]
            min.sort()
            particle = min[0][1]
            particle._is_selected = True
            self._selected = particle
            print particle
        
    def do_expose(self, widget, event):
        context = widget.window.cairo_create()
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()
        self.draw(context)
        return False
    
    KOLOR_TLA = (0,0,0) 
    KOLOR_CZASTKI = (0.3, 0.1, 0.1)
    KOLOR_ZAZNACZONEJ = (0.9, 0.1, 0.1)
        
    def draw(self, context=None):        
        '''
        Rysowanie widgetu.
        '''        
        rect = self.get_allocation()
        rect.x, rect.y = 0,0
        context.set_source_rgb(1, 1, 1)
        context.rectangle(rect)        
        context.fill_preserve()
        context.set_source_rgb(*self.KOLOR_TLA)
        context.stroke()  
           

        if(hasattr(self.model,'_agents')):
            pos = lambda agent, n: (agent._p[n]-self.getFunc2DBoundary()[n][0])*self._scalers[n]
            self._pos = pos
            for agent in self.model._agents: 
                if hasattr(agent, '_is_selected'):
                    context.set_source_rgb(*self.KOLOR_ZAZNACZONEJ)
                else:
                    context.set_source_rgb(*self.KOLOR_CZASTKI)    
                context.arc(pos(agent,0), pos(agent,1), 3, 0, 2*3.15)
                context.stroke()

    def redraw_canvas(self):
        if self.window:
            alloc = self.get_allocation()
            rect = gdk.Rectangle(0, 0, alloc.width, alloc.height)
            self.window.invalidate_rect(rect, True)
            self.window.process_updates(True)

   
    def updateScalers(self):
        B = self.getFunc2DBoundary()        
        b = self._window2dboundary
        try:            
            self._scalers = (float(b[2]-b[0])/(B[0][1]-B[0][0]),float(b[3]-b[1])/(B[1][1]-B[1][0]))
        except:
            self._scalers = (1, 1)
    
    def setModel(self, model):
        self.model = model
        self.updateScalers()

    def update(self):
        self.redraw_canvas()
        return True;
    
    def getFunc2DBoundary(self):
        return self.model.get_function().boundary   
