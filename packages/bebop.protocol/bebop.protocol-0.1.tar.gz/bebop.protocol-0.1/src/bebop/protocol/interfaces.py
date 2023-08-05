#!/usr/local/env/python
#############################################################################
# Name:         interfaces.py
# Purpose:      Defines protocols which simplify registrations
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import zope.interface
import zope.schema


class IProtocol(zope.interface.Interface):
    """A protocol registers components and provides decorators which allow
    to register these components from within Python. A protocol may be
    active or inactive within a set of modules.
    
    A component is registered immmediately if the protocol is active, 
    otherwise the registration is performed if the protocol is activated.
    """

    declarations = zope.schema.Dict(
        title=u'Declarations',
        description=u'A dict with module names as keys'\
                     ' and lists of declarations as values')

    activated = zope.schema.Set(
        title=u'Activated', 
        description=u'A set of modules in which the protocol was activated.')

    def __init__(name, provides=None):
        """Initializes the protocol.
        
        A name is required. You can specify an interface if all components 
        of the protocol share the same interface.
        """

    def __call__(*args, **kw):
        """Calls the component."""

    def declare(self, *args, **kw):
        """Adds a declaration to the protocol.
        
        The declaration is registered immediately if the protocol is 
        active in the relevant module.
        
        Otherwise the declaration is collected for later registration.
        """

    def configure(context, modules=None):
        """Activates all declarations within a ZCML configuration context."""

    def activate(modules=None):
        """Activates components of the protocol.
        
        If a set of modules is given the activation is restricted to these
        modules. Otherwise all components of the protocol are activated."""

    def deactivate(modules=None):
        """Deactivates (unregisters) the components of the protocol.
        
        If a set of modules is given the deactivation is restricted to these
        modules. Otherwise all components of the protocol are deactivated.
        """

    def record(self, context=None, modules=None):
        """Records the declarations as ZCML statements.
        
        If a set of modules is given the record is restricted to these
        modules. Otherwise all declarations of the protocol are recorded.
        """

