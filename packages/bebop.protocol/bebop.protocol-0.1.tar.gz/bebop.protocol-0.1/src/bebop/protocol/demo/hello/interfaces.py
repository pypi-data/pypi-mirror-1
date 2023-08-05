from zope.interface import Interface

class IGreetable(Interface): 
  def name(): 
     "Name of entity to greet." 
