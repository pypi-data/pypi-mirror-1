# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>
                Robert Niederreiter <rnix@squarewave.at>"""

import logging
from odict import OrderedDict
logger = logging.getLogger('xmlpolymerase.deserializer')

from exceptions import PolymeraseError

def deserialize(node, dictclass=OrderedDict, listclass=list, strip=False):
    """Deserialize a DOM into its simple python structure.
    
    >>> from xmlpolymerase.serializer import serialize
    >>> from xmlpolymerase.deserializer import deserialize
    
    single line string
    ------------------
    
    >>> teststructure = 'hello world'
    >>> node = serialize(teststructure, nodename='object')
    >>> structure = deserialize(node)
    >>> print structure
    hello world
    
    multi line string
    -----------------
    
    >>> from xmlpolymerase.serializer import serialize
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

    >>> teststructure = '''<?xml version="1.0"?>
    ... <object>
    ...   <node>
    ...     <one>a string</one>
    ...     <two></two>
    ...     <three><!-- a comment --></three>
    ...     <four type="bool">False</four>
    ...     <five type="list">
    ...       <entry>list element</entry>
    ...     </five>
    ...     <six><!-- a comment -->Text</six>
    ...   </node>
    ... </object>
    ... '''
    
    >>> from xml.dom.minidom import parseString
    >>> node = parseString(teststructure).childNodes[0]
    >>> structure = deserialize(node)
    >>> print structure
    OrderedDict([(u'node', OrderedDict([(u'one', 'a string'), (u'two', ''),
        (u'three', ''), (u'four', False), (u'five', ['list element']),
        (u'six', 'Text')]))])

    """
    # do we have a type explicit set?
    vtype = node.getAttribute('type')
    if not vtype:
        # filter
        childnodes = [cn for cn in node.childNodes \
                      if cn.nodeType in [node.ELEMENT_NODE, node.TEXT_NODE]]
        if not childnodes \
          or (len(childnodes) == 1 \
            and childnodes[0].nodeType == node.TEXT_NODE):
            vtype = 'string'
        elif len(node.childNodes) > 1:
            vtype = 'dict'
        else:
            raise PolymeraseError("No type found or guessed on import. abort")
    
    # proceed
    if vtype == 'list':
        data = listclass()
        for child in node.childNodes:
            if child.nodeType != child.ELEMENT_NODE:
                continue            
            if child.nodeName != 'entry':
                logger.warning('Found element != entry in list.')
                continue    
            data.append(deserialize(child, dictclass=dictclass, 
                                    listclass=listclass, strip=strip))
        return data
    if vtype == 'dict':
        data = dictclass()
        for child in node.childNodes:
            if child.nodeType != child.ELEMENT_NODE:
                continue
            key = child.tagName
            data[key] = deserialize(child, dictclass=dictclass, 
                                    listclass=listclass, strip=strip)
        return data    

    data = ''
    for child in node.childNodes:
        if child.nodeType != node.TEXT_NODE:
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
        if strip:
            data = data.strip()
    else:
        msg = 'Invalid type %s found on import, skipped.' % vtype
        raise PolymeraseError(msg)
    return data        