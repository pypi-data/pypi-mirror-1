#!/usr/local/env/python
#############################################################################
# Name:         browser.py
# Purpose:      View related protocols
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import sys
import os.path

from zope import interface
from zope import component

from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.app.publisher.browser import metadirectives
from zope.app.publisher.browser import viewmeta

import protocol
import interfaces


class PageDeclaration(protocol.FactoryDeclaration):
    """A page declaration 

    Substitutes the viewmeta.page directive. We use a FactoryDeclaration as
    the super class since the defined view class must be registered
    as a multiadapter.
    """

    directive = metadirectives.IPageDirective
    tagname = 'page'
    namespace = u'browser'
    
    class_ = None
    provides = IBrowserPage
    layer = IDefaultBrowserLayer
    allowed_interface = None
    allowed_attributes = None
    attribute='__call__'
    template=None
    menu = None
    title = None

    @property
    def module(self):
        obj = self.class_ or self.factory 
        return obj.__module__

    def configure(self, context):
        """Configures a page.
        
        Calls the viewmeta.page directive.
        """
        viewmeta.page(context, self.name, self.permission, self.for_,
                        layer=self.layer, template=self.template,
                        class_=self.class_, 
                        allowed_interface=self.allowed_interface,
                        allowed_attributes=self.allowed_attributes,
                        attribute=self.attribute, menu=self.menu,
                        title=self.title)

    def register(self):
        component.provideAdapter(factory=self.factory,
                                      provides=self.provides,
                                      adapts=(self.for_, IBrowserRequest),
                                      name=self.name)

    def unregister(self):
        component.globalSiteManager.unregisterAdapter(factory=self.factory,
                                      provided=self.provides,
                                      required=(self.for_, IBrowserRequest),
                                      name=self.name)


class PageProtocol(protocol.Protocol):
    """A page protocol which simplifies the declaration of browser pages."""
    declaration_factory = PageDeclaration


pageProtocol = PageProtocol('bebop.protocol.browser.page')

def _pages(cls):
    """Advice for the pages statement.
    
    Collects all page subdeclarations.
    """    
    pages_parameter = cls.__dict__['__pages_protocol__']
    del cls.__pages_protocol__
    page_list = cls.__dict__['__page_protocol_list__']
    del cls.__page_protocol_list__
    pages_parameter['factory'] = cls
    pages_parameter['class_'] = cls
    for page_parameter in page_list:
        kw = dict(pages_parameter)
        kw.update(page_parameter.__dict__)
        pageProtocol.declare(**kw)
    return cls    

def pages(*for_, **kw):
    """Protocol substitute for the browser pages directive. 
    
    Defines multiple pages without repeating all of the parameters.
    The pages directive allows multiple page views to be defined
    without repeating the 'for', 'permission', 'class', 'layer',
    'allowed_attributes', and 'allowed_interface' attributes.
    """
    
    frame = sys._getframe(1)
    locals = frame.f_locals
    
    if for_:
        if 'for_' in kw:
            raise TypeError("for can be used only if solely"\
                            "keyword parameters are used.")
        kw['for_'] = for_[0]
    # Try to make sure we were called from a class def. In 2.2.0 we can't
    # check for __module__ since it doesn't seem to be added to the locals
    # until later on.
    if (locals is frame.f_globals) or ('__module__' not in locals):
        raise TypeError("pages can be used only from a class definition.")

    locals['__pages_protocol__'] = kw
    locals['__page_protocol_list__'] = []
        
    interface.advice.addClassAdvisor(_pages)


def _page(cls):
    """Advice for the page statement.
    
    Collects all page subdeclarations.
    """
    if '__page_protocol__' in cls.__dict__:
        page_parameter = cls.__dict__['__page_protocol__']
        del cls.__page_protocol__
        page_parameter['factory'] = cls
        page_parameter['class_'] = cls
        pageProtocol.declare(**page_parameter)
    return cls    


class page(object):
    """Substitute for the browser page directive.
    
    Adds self to the list of page declarations.
    If called as a decorator it uses the function name
    as an implicitely specified attribute parameter and default name.
    """
    
    def __init__(self, *for_, **kw):
        frame = sys._getframe(1)
        locals = frame.f_locals
        if for_:
            if 'for_' in kw:
                raise TypeError("for can be used only "\
                                "if solely keyword parameters are used.")
            kw['for_'] = for_[0]
        self.__dict__.update(kw)
        if 'template' in kw:
            file = frame.f_globals['__file__']
            dir = os.path.dirname(file)
            path = os.path.abspath(os.path.join(dir, self.template))
            if not os.path.exists(path):
                raise ValueError("No such file", path)
            self.template = path
        
        if locals.get('__pages_protocol__'): 
            locals.setdefault('__page_protocol_list__', []).append(self)
        else:
            locals['__page_protocol__'] = kw
            interface.advice.addClassAdvisor(_page)


    def __call__(self, f):
        if hasattr(self, 'template'):
            raise TypeError("page can be used as a decorator "\
                            "only without template parameter.")
        self.attribute = f.func_name
        if not hasattr(self, 'name'):
            self.name = f.func_name
        return f

    
class GenericViewFunctionTraverser(object):
    """A view class that mimics the standard page traversal.
    
    Redirects the 'index.html' call to a generic function.
    """

    interface.implements(IPublishTraverse)
    
    def __init__(self, f):
        self.func = f
        
    def __call__(self, context, request):
        self.context = context
        self.request = request
        return self

    def callFunction(self):
        return self.func(self.context, self.request)
        
    def publishTraverse(self, request, name):
        if name == 'index.html':
            return self.callFunction
        raise NotFound(self.context, name)

class ViewFunction(protocol.GenericFunction):
    """A generic function that is registered as a view."""
    
    declaration_factory = protocol.AdapterDeclaration    

    provides = interface.Interface

    def __init__(self):
        super(ViewFunction, self).__init__(None, provides=self.provides)
        
    def when(self, for_, **kw):
        def decorator(f):
            traverser = GenericViewFunctionTraverser(f)
            traverser.__name__ = f.func_name
            traverser.__module__ = f.__module__
  
            self.declare(factory=traverser, 
                    for_=(for_, IBrowserRequest), 
                    provides=self.provides,
                    permission=kw.get('permission'),
                    name=kw['name'])
            
            return traverser

        return decorator


