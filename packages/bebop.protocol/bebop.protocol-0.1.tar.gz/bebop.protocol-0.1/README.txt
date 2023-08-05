Bebop Protocol
==============

This package contains a extension to Zope3 which simplifies the registration
of components.

Zope3 has been criticized as an overly complex and difficult to learn framework.
Especially the ZCML configuration language and the missing Python API for 
configuration actions has been a topic of debate.

This package tries to combine the conciseness of Python with the explicitness, 
fine-grained configurability, and conflict management of ZCML. A protocol is a 
Python object that defines how a component is registered and configured, how 
the component is called, and how it is unregistered. Protocols are used and 
extended by declarations, i.e. class advisors and decorators that correspond 
to existing ZCML directives. All declarations within a package can be activated 
with a single line of ZCML. The equivalent ZCML configuration can be recorded 
for documentary purposes and used as a basis for more selective configurations 
and overloads.

Since the protocol package mimics the ZCML directives as closely as possible 
it provides no extra learning curve for the experienced Zope3 programmer. 
Predefined protocols are available for adapters, utilities, subscribers, pages,
and menus. Since protocols are extensible, they can also be used to define 
generic functions and extend the component architecture with special forms 
of utilities and adapter lookup without the need to define new ZCML directives. 

