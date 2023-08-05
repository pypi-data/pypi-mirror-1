#This is a protocol extension that is used in the generic.txt

from bebop.protocol.generic_txt import count

@count.when(dict, permission='zope.View')
def count_dict(dict):
    return 2*len(dict)