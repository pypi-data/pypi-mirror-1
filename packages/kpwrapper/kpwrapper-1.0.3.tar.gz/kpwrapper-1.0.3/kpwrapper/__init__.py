# Copyright (c) 2009, Nokia Corp.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Nokia nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED THE COPYRIGHT HOLDERS AND CONTRIBUTORS ''AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import with_statement # for Python 2.5
from types import NoneType

__author__ = 'eemeli.kantola@iki.fi (Eemeli Kantola)'

import collections
import types

import Node_enhanced  # for the additional 'preconfigured' discovery method

from smart_m3.Node import Node, ParticipantNode, Query, Subscribe, M3_SUCCESS

debug = False

class _any(str):
    def __eq__(self, other):
        return other.__class__ is self.__class__ and str.__eq__(self, other) 

    def __cmp__(self, other):
        return cmp(self[:], other[:])

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self[:])

class uri(_any):
    '''URI node'''

class literal(_any):
    '''Literal value node'''

class bnode(_any):
    '''Temporary blank node'''

class_map = {'uri': uri, 'literal': literal, 'bnode': bnode}
def get_class(type_str):
    return class_map.get(type_str, str)

def to_typed_element(elem, deftype):
    return elem if isinstance(elem, (NoneType, _any)) else deftype(elem)

def listify(triples):
    if isinstance(triples, Triple):
        return [triples,]
    elif isinstance(triples, collections.Sequence):
        return triples if isinstance(triples, list) else list(triples)
    else:
        raise TypeError('The argument must be a Triple or Sequence, but %s was given' % type(triples))

def tuplify(triples):
    return [triple.to_tuple() for triple in listify(triples)]

def triplify(tuples):
    return [Triple.from_tuple(tuple) for tuple in tuples]

def wrap_if_not_none(type, o):
    return None if o is None else type(o)

def wrap_callback_handler(handler):
    '''Wraps a callback function in a Handler class, as expected by kp.Subscribe.subcribe_rdf().
    
    >>> def join_with_and(added, removed):
    ...     print('Added %s and removed %s' % (added, removed))
    >>> tuple = (('s', 'p', 'o'), 'uri', 'literal')
    >>> wrap_callback_handler(join_with_and).handle([tuple], [tuple])
    Added [Triple(uri('s'), uri('p'), literal('o'))] and removed [Triple(uri('s'), uri('p'), literal('o'))]

    >>> class MsgHandler:
    ...     def callback(self, added, removed):
    ...         join_with_and(added, removed)
    >>> wrap_callback_handler(MsgHandler()).handle([tuple], [tuple])
    Added [Triple(uri('s'), uri('p'), literal('o'))] and removed [Triple(uri('s'), uri('p'), literal('o'))]
    '''
    class CallbackHandlerWrapper:
        def __init__(self, handler):
            self.handler = handler
        
        def handle(self, added, removed):
            self.handler.callback(triplify(added), triplify(removed))

    if isinstance(handler, types.FunctionType):
        # Wrap the function inside a delegating class
        DelegatingCallbackHandler = type('DelegatingCallbackHandler', (),
                                         dict(callback = lambda self, added, removed: handler(added, removed)))
        handler_inst = DelegatingCallbackHandler()
    else:
        handler_inst = handler

    return CallbackHandlerWrapper(handler_inst)

def get_node_type_class(node_type):
    if isinstance(node_type, bool):
        return literal if node_type else uri
    else:
        return get_class(node_type)

class Triple:
    def __init__(self, subject, predicate, object):
        self.subject = to_typed_element(subject, uri)
        self.predicate = to_typed_element(predicate, uri)
        self.object = to_typed_element(object, literal)
    
    @staticmethod
    def from_tuple(tuple):
        """Initialize a Triple from a Python tuple.
        
        Triple(uri('subj'), uri('pred'), uri('obj'))
        >>> Triple.from_tuple((('subj', 'pred', 'obj'), 'literal', 'uri'))
        Triple(literal('subj'), uri('pred'), uri('obj'))
        >>> Triple.from_tuple((('subj', 'pred', 'obj'), 'uri'))
        Triple(uri('subj'), uri('pred'), uri('obj'))
        
        Wildcards are represented by corresponding classes:
        
        >>> Triple.from_tuple((('subj', None, None), 'literal', 'uri'))
        Triple(literal('subj'), None, None)
        >>> Triple.from_tuple(((None, None, None), None))
        Triple(None, None, None)

        Tuple's subject and object node types can also be represented by boolean
        values:

        >>> Triple.from_tuple((('subj', 'pred', 'obj'), False))
        Triple(uri('subj'), uri('pred'), uri('obj'))
        >>> Triple.from_tuple((('subj', 'pred', 'obj'), True, True))
        Triple(literal('subj'), uri('pred'), literal('obj'))

        """
        subject = tuple[0][0]
        predicate = tuple[0][1]
        object = tuple[0][2]
        s_type = get_node_type_class(tuple[1]) if len(tuple)==3 else str
        p_type = str
        o_type = get_node_type_class(tuple[2] if len(tuple)==3 else tuple[1])
        return Triple(wrap_if_not_none(s_type, subject),
                      wrap_if_not_none(p_type, predicate),
                      wrap_if_not_none(o_type, object))
    
    def to_tuple(self, default_stype = 'uri', default_otype = 'literal'):
        """Convert the Triple to a Python tuple.
        
        >>> Triple(uri('subj'), 'pred', literal('obj')).to_tuple()
        (('subj', 'pred', 'obj'), 'uri', 'literal')
        >>> Triple('subj', 'pred', uri('obj')).to_tuple()
        (('subj', 'pred', 'obj'), 'uri', 'uri')
        >>> Triple([1,2,3], None, False).to_tuple()
        (('[1, 2, 3]', None, 'False'), 'uri', 'literal')
        
        Wildcards:
        
        >>> Triple(uri('subj'), None, None).to_tuple()
        (('subj', None, None), 'uri', 'literal')
        >>> Triple(None, None, uri('foo')).to_tuple()
        ((None, None, 'foo'), 'uri', 'uri')
        """
        def get_typestr(obj, default=None):
            if isinstance(obj, type) and issubclass(obj, _any):
                return obj.__name__
            elif isinstance(obj, _any):
                return obj.__class__.__name__
            else:
                return default
        
        tuple = ((wrap_if_not_none(str, self.subject),
                  wrap_if_not_none(str, self.predicate),
                  wrap_if_not_none(str, self.object)),)

        s_typestr = get_typestr(self.subject, default_stype)
        if s_typestr is not None:
            tuple += (s_typestr,)
        
        tuple += (get_typestr(self.object, default_otype),)
        return tuple
    
    def __getitem__(self, index):
        return (self.subject, self.predicate, self.object)[index]
    
    def __repr__(self):
        return "Triple(%s, %s, %s)" % (repr(self.subject), repr(self.predicate), repr(self.object))

    def __hash__(self):
        """
        >>> hash(Triple('a', 'b', 'c')) == hash(Triple('a', 'b', 'c'))
        True
        >>> hash(Triple('a', 'b', 'c')) == hash(Triple(uri('a'), 'b', 'c'))
        True
        """
        return hash(self.subject) | hash(self.predicate) | hash(self.object)

    def __eq__(self, other):
        """
        >>> Triple('a', 'b', literal('c')) == Triple('a', 'b', literal('c'))
        True
        >>> Triple('a', 'b', 'c') == Triple(literal('a'), 'b', 'c')
        False
        """
        return (other.__class__ is Triple and
                self.subject == other.subject and self.predicate == other.predicate and self.object == other.object)

    def __cmp__(self, other):
        """
        >>> cmp(Triple(uri('a'), 'b', 'c'), Triple('a', 'b', literal('c'))) == 0
        True
        >>> cmp(Triple('a', 'a', 'c'), Triple('a', 'b', literal('c'))) < 0
        True
        >>> cmp(Triple('a', 'b', 'c'), Triple('a', 'b', literal('b'))) > 0
        True
        """
        c = cmp(self.subject, other.subject)
        if c != 0: return c
        c = cmp(self.predicate, other.predicate)
        if c != 0: return c
        c = cmp(self.object, other.object)
        return c

class TransactionWrapper:
    def __init__(self, node, create_method, close_method, handle):
        self.node = node
        self._create_method = create_method
        self._close_method = close_method
        self.handle = handle
        self.tx = None
    
    def __enter__(self):
        self.open()
        return self.tx

    def __exit__(self, type, value, traceback):
        self.close()
    
    def open(self):
        self.tx = self._create_method(self.node, self.handle)
        if (debug):
            print('Created %s transaction' % self.tx.__class__.__name__)
    
    def close(self):
        # Work around bugs in Node when closing connection
        if (isinstance(self.tx, Query) and not hasattr(self.tx.conn, 's') or
            isinstance(self.tx, Subscribe) and not hasattr(self.tx, 'sub_id')):
            
            if (debug):
                print('Not actually closing anything due to a bug in %s' % self.tx.__class__.__name__)
        else:
            self._close_method(self.node, self.tx)
        
        if (debug):
            print('Closed %s transaction' % self.tx.__class__.__name__)
        self.tx = None

class SIBConnection(object):
    '''
    Object oriented and pythonified wrapper around Node and the transactions
    '''
    
    def __init__(self, node_name='Node', method='Manual'):
        self.node = ParticipantNode(node_name)
        self.handle = self.node.discover(method=method, browse=False)
        self.last_result = None
    
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def open(self):
        self.last_result = self.node.join(self.handle)
        if not self.last_result:
            raise Exception('Could not join the Smart Space')
        return self.last_result

    def close(self):
        self.last_result = self.node.leave(self.handle)
        return self.last_result

    def _wrap_tx(self, create_method, close_method):
        return TransactionWrapper(self.node, create_method, close_method, self.handle)

    def insert_tx(self):
        return self._wrap_tx(Node.CreateInsertTransaction, Node.CloseInsertTransaction)

    def query_tx(self):
        return self._wrap_tx(Node.CreateQueryTransaction, Node.CloseQueryTransaction)
    
    def update_tx(self):
        return self._wrap_tx(Node.CreateUpdateTransaction, Node.CloseUpdateTransaction)
    
    def remove_tx(self):
        return self._wrap_tx(Node.CreateRemoveTransaction, Node.CloseRemoveTransaction)

    def subscribe_tx(self):
        return self._wrap_tx(Node.CreateSubscribeTransaction, Node.CloseSubscribeTransaction)

    def insert(self, triples, **kwargs):
        with self.insert_tx() as tx:
            self.last_result = tx.send(tuplify(triples), **kwargs)

        return (isinstance(self.last_result, collections.Sequence)
                and len(self.last_result) > 0
                and self.last_result[0] == M3_SUCCESS)

    def query(self, query):
        with self.query_tx() as tx:
            return triplify(tx.rdf_query(query.to_tuple(), return_subj_type=True))

    def update(self, r_triples, i_triples):
        with self.update_tx() as tx:
            self.last_result = tx.update(tuplify(i_triples), 'rdf-m3',
                                         tuplify(r_triples), 'rdf-m3',
                                         confirm=True)

        return (isinstance(self.last_result, collections.Sequence)
                and len(self.last_result) > 0
                and self.last_result[0] == M3_SUCCESS)

    def remove(self, triples):
        '''Removes a list of triples. Note: remove does not currently support wildcards!'''
        with self.remove_tx() as tx:
            self.last_result = tx.remove(tuplify(triples), confirm=True)
        
        return self.last_result == M3_SUCCESS

    def subscribe(self, triples, handler):
        '''Add subscription and register handler as the callback handler.
        
        handler an be:
         - a function taking two arguments: added and removed
         - class that defines a method 'callback', taking two arguments: added and removed'''
        tw = self.subscribe_tx()
        tw.open()
        self.last_result = tw.tx.subscribe_rdf(tuplify(triples), wrap_callback_handler(handler), True)
        return tw if self.last_result is not None else None
