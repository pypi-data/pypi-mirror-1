import zope.interface

class ISampleClass(zope.interface.Interface):
    """A sample content class."""
        
    def foo():
        """Test method."""
 
class IProtectedMethods(zope.interface.Interface):
    """A protected interface."""

    def protected():
        """A public method."""

class IPublicMethods(zope.interface.Interface):
    """A public interface."""
    
    def public():
        """A public method."""

class ISampleEvent(zope.interface.Interface):
    """A sample event."""

class ISample(zope.interface.Interface):
    """A sample interface."""
    
class ISampleUtility(zope.interface.Interface):
    """A sample utility."""

class ISampleComponentUtility(zope.interface.Interface):
    """A sample component utility."""
    
class INamedSampleUtility(zope.interface.Interface):
    """A named sample utility."""