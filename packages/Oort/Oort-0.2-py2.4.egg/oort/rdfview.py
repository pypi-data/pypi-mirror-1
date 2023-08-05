#=======================================================================
import rdflib
from rdflib import RDF, Namespace, Graph, BNode
try: import simplejson
except ImportError: simplejson = None
from oort.util.code import contract
#=======================================================================
# TODO: mark steps and query/selector call points.


THIS_QUERY = object()
DEFAULT_MAX_DEPTH = 20


# TODO: optimization by providing an "execution context" and avoiding multiple queries for the same uri etc.
# FIXME: complete; pass along execContext (and maxDepth?)
def run_queries(queries, graph, subject, lang):
    execContext = {}
    for query in queries:
        key = (id(query), str(subject))
        if key not in execContext:
            execContext[key] = query(graph, subject, lang)
        yield execContext[key]


#=======================================


class Selector(object):
    __slots__ = ('predicate', 'namespace', 'subQuery', 'filter',
                 'name', 'queryClass')

    def __init__(self, base, subQuery=None):
        if isinstance(base, Namespace):
            self.namespace = base
            self.predicate = None
        else:
            self.namespace = None
            self.predicate = base
        self.subQuery = subQuery
        self.filter = None

    @contract.state_change
    def hook_into_rdf_query(self, name, queryClass):
        self.name = name
        self.queryClass = queryClass
        if not self.predicate and self.namespace:
            self.predicate = self.namespace[name]

    def __get__(self, queryObj, _cls=None):
        prep = queryObj._preparedSelects[self.name]
        if not prep.hasRun:
            result = self._process_for_subqueries(
                    self.select(*prep.selectArgs),
                    *prep.selectArgs[:2]
                )
            prep.hasRun = True
            prep.result = result
        return prep.result

    # TODO: if subQuery is None but resource isn't a literal, use rdf:type to
    # find a proper RdfQuery (by looking in a register of RdfQuery subclasses
    # with a declared SCHEMA)? Or is type_switch enough?
    def _process_for_subqueries(self, rawresults, graph, lang):
        returnList = isinstance(rawresults, list)
        if not rawresults:
            if returnList: return []
            else: return None

        subQuery = self.subQuery
        if not subQuery:
            return rawresults
        else:
            # FIXME: using THIS_QUERY may currently cause infinite loops.
            if subQuery is THIS_QUERY:
                subQuery = self.queryClass

            if returnList:
                return [subQuery(graph, lang, uri) for uri in rawresults]
            else:
                return subQuery(graph, lang, rawresults)

    @contract.template_method
    def select(self, graph, lang, subject, predicate):
        raise NotImplementedError
        return None or []

    @contract.default_method
    def reverse(self, graph, subject, predicate, value):
        pass

    def __rshift__(self, subQuery):
        self.subQuery = subQuery
        return self

    def __or__(self, filter):
        self.filter = filter
        return self


class PreparedSelect:
    __slots__ = ('graph', 'subject', 'lang',
                 'result', 'hasRun')
    def __init__(self, graph, lang, subject, predicate):
        self.selectArgs = graph, lang, subject, predicate
        self.result = None
        self.hasRun = False # TODO: make configurable?


class _rdf_query_meta(type):
    def __init__(cls, clsName, bases, clsDict):
        type.__init__(cls, clsName, bases, clsDict)

        selectors = cls._selectors = {}
        for base in bases:
            if hasattr(base, '_selectors'):
                selectors.update(base._selectors)

        for key, value in clsDict.items():
            if isinstance(value, Selector):
                value.hook_into_rdf_query(key, cls)
                selectors[key] = value

        # TODO: remove unless something useful is implemented!
        # ..  likt opt. SCHEMA and/or type as a resource filter (thus not
        # querying more if resource is not of the given type)
        #SCHEMA = clsDict.get('SCHEMA')
        #if not SCHEMA:
        #    for base in bases:
        #        if hasattr(base, 'SCHEMA'): SCHEMA = base.SCHEMA; break


class RdfQuery(object):
    __metaclass__ = _rdf_query_meta

    def __init__(self, graph, lang, subject, depth=DEFAULT_MAX_DEPTH):
        # TODO: pass depth and use to avoid infinite recursion
        if depth == 0:
            raise NotImplementedError("TODO: max depth exception..")

        self._graph = graph
        self._subject = subject
        self._lang = lang
        prepareds = self._preparedSelects = {}
        for name, selector in self._selectors.items():
            if not subject: # FIXME: happens when subject is a bnode?
                setattr(self, name, None)
                continue
            prep = PreparedSelect(graph, lang, subject, selector.predicate)
            prepareds[name] = prep

    def __str__(self):
        return str(self._subject)

    def get_selected_value(self, name):
        return self._preparedSelects[name].result

    def to_graph(self, lgraph=None):
        subject = self._subject or BNode() # FIXME: is this ok?
        if not subject: return # FIXME, see fixme in __init__

        lgraph = lgraph or Graph()

        for t in self._graph.objects(subject, RDF.type):
            lgraph.add((subject, RDF.type, t))

        for selector in self._selectors.values():
            predicate = selector.predicate
            value = selector.__get__(self)
            if not value:
                continue
            selector.reverse(lgraph, subject, predicate, value)

        # FIXME: why is this happening; how can we prevent it?
        for t in lgraph:
            if None in t: lgraph.remove(t)
        return lgraph

    def to_rdf(self):
        return self.to_graph().serialize(format='pretty-xml')

    def to_dict(self, keepSubject=False):
        d = {}
        if keepSubject:
            subjectKey = isinstance(keepSubject, str) and keepSubject or 'resource'
            subj = self._subject
            if subj and not isinstance(subj, BNode):
                d[subjectKey] = self._subject

        for selector in self._selectors.values():
            name = selector.name
            value = selector.__get__(self)
            if not value:
                continue
            if isinstance(value, dict):
                d[name] = dict([(key, self.__dict_convert(val, keepSubject))
                            for key, val in value.items()])
            elif hasattr(value, '__iter__'):
                d[name] = [self.__dict_convert(val, keepSubject)
                            for val in value]
            else:
                d[name] = self.__dict_convert(value, keepSubject)
            # TODO: handle xml literals
        return d

    def __dict_convert(self, value, keepSubject):
        if isinstance(value, RdfQuery):
            return value.to_dict(keepSubject)
        else:
            return unicode(value) # TODO: simple type conversions?

    def to_json(self, keepSubject=False):
        if simplejson:
            return simplejson.dumps(self.to_dict(keepSubject))
        else:
            raise NotImplementedError


#=======================================


# TODO: totally untested!
#def type_switch(typeSelectors, default):
#    rdfType = graph.value(resource, RDF.type, None, any=True)
#    def select(graph, resource, lang):
#        return typeSelectors.get(rdfType, default)
#    return select



def back_from_value(graph, subject, predicate, value):
        if isinstance(value, RdfQuery):
            graph.add((subject, predicate, value._subject))
            value.to_graph(graph)
        else:
            if not isinstance(value, list): # TODO: fix this
                graph.add((subject, predicate, value))

class LiteralSelector(Selector):
    def reverse(self, graph, subject, predicate, value):
        back_from_value(graph, subject, predicate, value)

class EachSelector(Selector):
    def reverse(self, graph, subject, predicate, values):
        for value in values:
            back_from_value(graph, subject, predicate, value)



class one(LiteralSelector):
    def select(self, graph, lang, subject, predicate):
        return graph.value(subject, predicate, None, any=True)


class each(EachSelector):
    def select(self, graph, lang, subject, predicate):
        return list(graph.objects(subject, predicate))


class collection(Selector):
    def __init__(self, base, subQuery=None, multiple=False):
        Selector.__init__(self, base, subQuery)
        self.multiple = multiple

    def select(self, graph, lang, subject, predicate):
        if self.multiple:
            allItems = [graph.items(res) for res in graph.objects(subject, predicate)]
            return list(chain(*allItems))
        else:
            return list(graph.items(graph.value(subject, predicate, None, any=True)))

    def reverse(self, graph, subject, predicate, values):
        if not values:
            graph.add((subject, predicate, RDF.nil))
            return
        bnode = BNode()
        graph.add((subject, predicate, bnode))
        for value in values:
            back_from_value(graph, bnode, RDF.first, value)
            newBnode = BNode()
            graph.add((bnode, RDF.rest, newBnode))
            bnode = newBnode
        graph.add((bnode, RDF.rest, RDF.nil))


class localized(LiteralSelector):
    def select(self, graph, lang, subject, predicate):
        first = None
        for value in graph.objects(subject, predicate):
            if not first: first = value
            if getattr(value, 'language', None) == lang:
                return value
        return first


# TODO: this is a hackish solution; see also below (transparently using datatype)
from oort.etreeutil import language_filtered_xml
class localized_xml(LiteralSelector):
    def select(self, graph, lang, subject, predicate):
        return language_filtered_xml(graph.objects(subject, predicate), lang)


class i18n_dict(Selector):
    def select(self, graph, lang, subject, predicate):
        valueDict = {}
        for value in graph.objects(subject, predicate):
            valueDict[value.language] = value
        return valueDict

    def reverse(self, graph, subject, predicate, value):
        # FIXME: test if this really works..
        back_from_value(graph, subject, predicate, value)


class each_localized(EachSelector):
    def select(self, graph, lang, subject, predicate):
        return [ value for value in graph.objects(subject, predicate)
                 if value.language == lang ]


#=======================================


# FIXME: just hacked it to work after major refactoring..
class WrapperSelector(Selector):
    def __get__(self, queryObj, _cls=None):
        prep = queryObj._preparedSelects[self.name]
        if not prep.hasRun:
            prep.result = self.selectImpl(queryObj, *prep.selectArgs)
            prep.hasRun = True
        return prep.result

def selector(func):
    "Use as decorator for methods of an RdfQuery subclass to convert them to selectors."
    selector = WrapperSelector(None)
    selector.selectImpl = func
    return selector


#=======================================
# TODO: consider returning ElementTree data for XML Literals. And if so, also
# filtered on u'{http://www.w3.org/XML/1998/namespace}lang' (keep if none) for localized.
# TODO: also consider checking datatype and coercing (at least) these:
#   NOTE: use rdflib.sparql.sparqlOperators.getLiteralValue(v)
#         seeAlso <http://en.wikipedia.org/wiki/RDFLib#RDF_Literal_Support>
#XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
#XSD['string']
#XSD['integer']
#XSD['long']
#XSD['double']
#XSD['float']
#XSD['decimal']
#XSD['dateTime']
#XSD['date']
#XSD['time']


#=======================================

def chain(*iters):
    for iter in iters:
        for i in iter: yield i


