# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.interface import implements
from gocept.objectquery.interfaces import IQueryProcessor


class QueryProcessor(object):
    """ Processes a query to the collection and returns the results.

    QueryProcessor parses a query with the given parser. It returns a
    list with resulting objects from the given collection.

    """

    implements(IQueryProcessor)


    def __init__(self, parser, collection):
        self.collection = collection
        self.parser = parser

    def __call__(self, expression):
        """ Process expression and return a queryplan. """
        qp = self.parser.parse(expression)
        result = self._process_qp(qp)
        return self._oids2objects(result)

    def _process_qp(self, qp):
        """ Recursive process of query plan ``qp``. """
        if not qp:
            return None
        func = getattr(self, "_process_" + qp[0])
        return func(*qp[1:])

    def _process_ELEM(self, *args):
        """ Return all elements from ClassIndex with matching name. """
        return self.collection.by_class(args[0])

    def _process_WILDCARD(self, *args):
        """ Return all elements from ClassIndex. """
        return self.collection.all()

    def _process_EAJOIN(self, *args):
        """ Element-Attribute-Join. """
        elemlist = self._process_qp(args[1])
        return self.collection.eajoin(elemlist, *args[0][1])

    def _process_EEJOIN(self, elemlist1, elemlist2, elemlist2a=None):
        """ Element-Element-Join. """
        kcwild = None
        if elemlist2 == '/_*/':
            elemlist2 = elemlist2a
            kcwild = True
        elemlist1 = self._process_qp(elemlist1)
        if elemlist1 is None:
            elemlist1 = [self.collection.root._p_oid]
        elemlist2 = self._process_qp(elemlist2)
        return self.collection.eejoin(elemlist1, elemlist2, kcwild)

    def _process_KCJOIN(self, *args):
        """ Element-Occurence-Join. """
        elemlist = self._process_qp(args[1])
        return self._remove_duplicates(
                        self.collection.kcjoin(elemlist, args[0]))

    def _process_UNION(self, *args):
        """ Union of two results. """
        return self.collection.union(self._process_qp(args[0]),
                                            self._process_qp(args[1]))

    def _process_PREC(self, *args):
        """  """
        result = self._process_qp(args[0])
        return [ (elem[1], elem[1]) for elem in result ]

    def _remove_duplicates(self, list):
        returnlist = []
        for elem in list:
            if elem not in returnlist:
                returnlist.append(elem)
        return returnlist

    def _oids2objects(self, oidlist):
        """ Convert the oidlist to objectlist. """
        result = []
        for oid in oidlist:
            result.append(self.collection._p_jar.get(oid[1]))
        return self._remove_duplicates(result)
