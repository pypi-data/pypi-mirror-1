from persistent import Persistent 
from zope.publisher.browser import BrowserView 

from bebop.protocol import protocol
from bebop.protocol import browser

class World(Persistent): 
    pass

greet = protocol.GenericFunction('IGreet')
@greet.when(World)
def greet_world(world):
    return 'world'

class Greeting(BrowserView): 
    browser.page(World, name="greet", permission='zope.Public')
  
    def __call__(self): 
        return "Hello %s" % greet(self.context) 

