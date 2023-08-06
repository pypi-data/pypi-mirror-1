###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
ParseTree

$Id: parsetree.py 2054 2009-03-14 10:11:29Z ajung $
"""

from zope.interface import implements
from zopyx.txng3.core.interfaces import IParseTreeNode

class BaseNode:
    """ base class for all nodes """

    implements(IParseTreeNode)

    def __init__(self, v, field=None):
        if isinstance(self.__class__, BaseNode):
            raise ImplementationError("Can't instantiate BaseNode")
        self._field = field
        self.setValue(v)
        self._parent = None

    def getType(self): 
        return self.__class__.__name__

    def getValue(self): 
        return self._value

    def getField(self):
        return self._field

    def setValue(self, value): 

        if isinstance(value, (list, tuple)):
            for v in value: 
                if issubclass(v.__class__, BaseNode):
                    v._parent = self

        self._value = value

    def sameAs(self, node):
        return bool(self.getType()==node.getType() and  self.getValue()==node.getValue()) 
           
    def __repr__(self):
        if self._field:
            return "%s(%s::%r)" % (self.__class__.__name__, self.getField(), self.getValue())
        else:
            return "%s(%r)" % (self.__class__.__name__, self.getValue())


class WordNode(BaseNode): pass
class GlobNode(BaseNode): pass
class TruncNode(BaseNode): pass
class SubstringNode(BaseNode): pass
class LTruncNode(BaseNode): pass
class SimNode(BaseNode): pass
class NotNode(BaseNode): pass
class AndNode(BaseNode): pass
class OrNode(BaseNode): pass
class NearNode(BaseNode): pass
class PhraseNode(BaseNode): pass
class RangeNode(BaseNode): pass



def stopword_remover(node, stopwords):
    """ removes all WordNodes that represent a stopword from the query """

    v = node.getValue()

    if isinstance(v, (list, tuple)):
        node.setValue([child for child in v if not(isinstance(child, WordNode) and child.getValue().lower() in stopwords)])
        for child in node.getValue():
            stopword_remover(child, stopwords)

    elif isinstance(v, BaseNode):
        stopword_remover(v, stopwords)


def flatten_NearNode(node, lst=[]):
    """ return a sequence of all Wordnodes within a NearNode subtree. We need this
        because the current query parser creates only a nested tree of NearNodes
        instead of a flat list.
    """                         

    if isinstance(node, WordNode):
        lst.append(node)

    elif isinstance(node, NearNode):
        flatten_NearNode(node.getValue(), lst)

    elif isinstance(node, (list, tuple)):
        for child in node:
            flatten_NearNode(child, lst)

    return lst
