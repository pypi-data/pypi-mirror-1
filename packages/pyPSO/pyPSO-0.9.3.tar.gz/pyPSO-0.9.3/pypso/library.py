#-*- coding: utf-8 -*-
'''
Biblioteka, w tym module są przechowywana załadowane strategie, oraz funkcje.
'''

#indeksy kolumn
( FUNCTION, NAME, DOCUMENTATION ) = range(3)

class _library:
    def __init__(self):
        self.__elements = []
        self.__elements_index = {}
    
    def register(self, element, name=None, documentation=None):
        if name==None:
            name = element.__name__
        if documentation==None:
            documentation = element.__doc__
        el = (element, name, documentation)
        self.__elements.append(el)
        self.__elements_index[name]= el
        
        
    def get(self,name=None,function=None):    
        if name!=None:
            return self.__elements_index[name]        
        if function!=None:
            for element in self.__elements:
                if element[0]==function:
                    return element
            return None
        return self.__elements
        
function_library = _library()
strategy_library = _library()