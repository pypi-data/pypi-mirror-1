# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

import logging
from odict import OrderedDict
logger = logging.getLogger('xmlpolymerase.deserializer')

def deserialize(node, dictclass=OrderedDict, listclass=list):
    """Deserialize a DOM into its simple python structure.
    
    >>> from serializer import serialize
    >>> from deserializer import deserialize
    
    single line string
    ------------------
    
    >>> teststructure = 'hello world'
    >>> node = serialize(teststructure, nodename='object')
    >>> structure = deserialize(node)
    >>> print structure
    hello world
    
    multi line string
    -----------------
    
    >>> from serializer import serialize
    >>> teststructure = '''hello world,
    ... and universe,
    ... 
    ... and whats else outside.'''
    >>> node = serialize(teststructure, nodename='object')    
    >>> structure = deserialize(node)
    >>> print structure
    hello world,
    and universe,
    <BLANKLINE>
    and whats else outside.
    
    list
    ----
    
    >>> teststructure = ['hello world', 'hello universe']
    >>> node = serialize(teststructure, nodename='object')
    >>> structure = deserialize(node)
    >>> print structure
    ['hello world', 'hello universe']
    
    a dict
    ------
    
    for testing we need some ordered dict (from pythonutils).
    
    >>> from odict import OrderedDict

    >>> teststructure = OrderedDict()
    >>> teststructure['one'] = 'Eins'
    >>> teststructure['two'] = 'Zwei'
    >>> teststructure['three'] = 'Drei'
    
    go more complex!
    >>> teststructure['four'] = [True, 2, '3', 4.0]
    >>> node = serialize(teststructure, nodename='object')    
    >>> structure = deserialize(node)
    >>> print structure
    OrderedDict([('one', 'Eins'), ('two', 'Zwei'), ('three', 'Drei'), ('four', [True, 2, '3', 4.0])])
    
        
    """
    # do we have a type explicit set?
    vtype = node.getAttribute('type')
    if not vtype:
        if len(node.childNodes) == 1 and node.childNodes[0].nodeName == '#text':
            vtype = 'string'
        elif len(node.childNodes) > 1:
            vtype = 'dict'
        else:
            logger.warning('No type found or guessed on import, skipped.')
            return
    
    # proceed
    if vtype == 'list':
        data = listclass()
        for child in node.childNodes:
            if child.nodeName != 'entry':
                logger.warning('Found element != entry in list.')
                continue    
            data.append(deserialize(child, dictclass=dictclass, 
                                    listclass=listclass))
        return data
    if vtype == 'dict':
        data = dictclass()
        for child in node.childNodes:
            key = child.tagName
            data[key] = deserialize(child, dictclass=dictclass, 
                                    listclass=listclass)
        return data    

    data = ''
    for child in node.childNodes:
        if child.nodeName != '#text':
            continue
        lines = [ line.lstrip() for line in child.nodeValue.splitlines() ]
        data += '\n'.join(lines)
        
    if vtype == 'bool':
        if data == 'True':
            data = True
        else:
            data = False
    elif vtype == 'int':
        data = int(data)
    elif vtype == 'float':
        data = float(data)
    elif vtype == 'string':
        data = str(data)
    else:
        logger.warning('Invalid type %s found on import, skipped.' % vtype)
        return None
    return data        