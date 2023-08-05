# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

import types
from xml.dom.minidom import getDOMImplementation
import logging
logger = logging.getLogger('xmlpolymerase.serializer')

def serialize(data, node=None, nodename=None):
    """Serialize a simple python structure into a DOM representation.
    
    >>> from serializer import serialize
    
    simple string
    -------------
    
    >>> teststructure = 'hello world'
    >>> node = serialize(teststructure, nodename='object')
    >>> print node.toprettyxml()
    <object>
        hello world
    </object>
    <BLANKLINE>
    
    multiline string
    ----------------
    
    >>> from serializer import serialize
    >>> teststructure = '''hello world,
    ... and universe,
    ... 
    ... and whats else outside.'''
    >>> node = serialize(teststructure, nodename='object')
    >>> print node.toprettyxml()
    <object>
        hello world,
    and universe,
    <BLANKLINE>
    and whats else outside.
    </object>
    <BLANKLINE>

    list
    ----
    
    >>> teststructure = ['hello world', 'hello universe']
    >>> node = serialize(teststructure, nodename='object')
    >>> print node.toprettyxml()
    <object type="list">
        <entry>
                hello world
        </entry>
        <entry>
                hello universe
        </entry>
    </object>
    <BLANKLINE>
    
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
    >>> print node.toprettyxml()
    <object>
        <one>
                Eins
        </one>
        <two>
                Zwei
        </two>
        <three>
                Drei
        </three>
        <four type="list">
                <entry type="bool">
                        True
                </entry>
                <entry type="int">
                        2
                </entry>
                <entry>
                        3
                </entry>
                <entry type="float">
                        4.0
                </entry>
        </four>
    </object>
    <BLANKLINE>
    
    """
    if node is None and nodename is None:
        raise ValueError, 'You have either to provide a node or a nodename.'
    # create a document, its our factory
    dom = getDOMImplementation()
    doc = dom.createDocument(None, nodename or 'root', None)    
    if node is None:
        # create a document set it root node 
        node = doc.childNodes[0]
        
    if isinstance(data, (tuple, list)):
        node.setAttribute('type', 'list')                
        for value in data:                    
            element = doc.createElement('entry')
            serialize(value, element)
            node.appendChild(element)
        return node
        
    if isinstance(data, (dict,)):            
        for key in data.keys():
            element = doc.createElement(key)
            serialize(data[key], element)
            node.appendChild(element)
        return node
        
    if type(data) is types.BooleanType:
        node.setAttribute('type', 'bool')                
        data = str(data)
    elif type(data) is types.IntType:
        node.setAttribute('type', 'int')                                    
        data = str(data)
    elif type(data) is types.FloatType:
        node.setAttribute('type', 'float')                                    
        data = str(data)
    elif type(data) in types.StringTypes:
        pass
        # its ok, but we dont need an attribute, because its default
    else:
        logger.warn('Invalid type %s found for key %s, skipped.'%\
                    (type(data), key))
        return
        
    child = doc.createTextNode(data)
    node.appendChild(child)
    return node