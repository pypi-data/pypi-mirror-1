#A module that uses the class protocol
import zope.interface
from bebop.protocol import protocol

import interfaces

class SampleClass(object):
    zope.interface.implements(
        interfaces.ISampleClass,
        interfaces.IPublicMethods,
        interfaces.IProtectedMethods)

    protocol.factory(id='bebop.protocol.demo.package.security.SampleClass')
        
    # an interface can be provided as a keyword parameter ...
    protocol.require(
        permission="zope.View",
        interface=interfaces.ISampleClass)
    
    # or a positional parameter
    protocol.require(interfaces.IProtectedMethods,
        permission="zope.MangeContent")

    protocol.allow(interfaces.IPublicMethods)

    protocol.require(
        set_attributes=['protected_attribute'], 
        permission="zope.MangeContent")
 
    protected_attribute = 0
    
    def public(self):
        print "public method called"
        
    def protected(self):
        print "protected method called"
