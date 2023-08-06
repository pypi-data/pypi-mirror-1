'''
Created on 22.06.2009

@author: falko
'''
from zope.component.interfaces import IView
from zope.interface.interface import Interface

class IExtDirectView(IView):
    """Ext.Direct View"""
    
class IDirectConfig(Interface):
    """Ext.Direct Config Adapter"""
    def __call__():
        pass
    
class IDirectProvider(Interface):    
    def __call__(directRequest):
        pass
    
