# -*- coding: UTF-8 -*-
"""This module contains a system for creating rdf query classes in a mainly 
declarative manner. These are built by subclassing ``RdfQuery`` and creating 
class attributes by using ``Selector``:s. There are several selectors provided 
in this module to cover all regular cases of data acquisition.
"""
#=======================================================================
from rdflib import RDF, RDFS, Namespace, URIRef, BNode, Literal
from rdflib import ConjunctiveGraph
from types import ModuleType
try: import simplejson
except ImportError: simplejson = None
from oort.util.code import contract
#=======================================================================


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
    __slots__ = ('predicate', '_namespace', 'subQuery', 'filters',
                 '_name', '_queryClass')

    def __init__(self, predBase=None, subQuery=None):
        self.predicate = None
        self._namespace = None
        if isinstance(predBase, Namespace) or isinstance(predBase, ModuleType):
            self._namespace = predBase
        elif isinstance(predBase, URIRef):
            self.predicate = predBase
        self.subQuery = subQuery
        self.filters = []

    @contract.state_change
    def hook_into_rdf_query(self, name, queryClass):
        self._name = name
        self._queryClass = queryClass
        if self.subQuery is THIS_QUERY:
            self.subQuery = self._queryClass
        if not self._namespace:
            self._namespace = queryClass._namespace
        if not self.predicate and self._namespace:
            if isinstance(self._namespace, ModuleType):
                self.predicate = getattr(self._namespace, name)
            else:
                self.predicate = self._namespace[name]
        # TODO: not used since e.g. the selector decorator uses no predicate
        #if not self.predicate:
        #    raise ValueError(
        #            "Could not determine predicate for Selector %s" % self)

    def __get__(self, parentQuery, _parentQueryClass=None):
        prep = parentQuery._preparedSelects[self._name]
        if not prep.hasRun:
            result = self.retreive_result(parentQuery, prep.selectArgs)
            for fltr in self.filters:
                result = fltr(result)
            prep.hasRun = True
            prep.result = result
        return prep.result

    @contract.default_method
    def retreive_result(self, parentQuery, selectArgs):
        result = self._process_for_subqueries(
                self.select(*selectArgs),
                *selectArgs[:2]
            )
        return result

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
            if returnList:
                return [subQuery(graph, lang, uri) for uri in rawresults]
            else:
                return subQuery(graph, lang, rawresults)

    @contract.template_method
    def select(self, graph, lang, subject):
        raise NotImplementedError
        return None or []

    @contract.default_method
    def back_to_graph(self, graph, subject, value):
        pass

    def __rshift__(self, subQuery):
        self.subQuery = subQuery
        return self

    def __or__(self, fltr):
        self.filters.append(fltr)
        return self

    def __set__(self, parentQuery, value):
        prep = parentQuery._preparedSelects[self._name]
        lang = parentQuery._lang
        sub = self.subQuery
        if isinstance(value, list):
            value = [self.type_raw_value(val, lang) for val in value]
        else:
            value = self.type_raw_value(value, lang)
        if sub:
            if isinstance(value, list):
                prep.result = [sub.from_dict(val, lang, BNode())
                                for val in value]
            else:
                prep.result = sub.from_dict(value, lang, BNode())
        else:
            prep.result = value
            prep.hasRun = True

    @contract.default_method
    def type_raw_value(self, value, lang):
        # TODO: need more clever type mapping. also, allow {'_uri': ".." } to be resource?
        if isinstance(value, str.__base__):
            value = Literal(value)
        return value


class PreparedSelect(object):
    __slots__ = ('selectArgs', 'result', 'hasRun')
    def __init__(self, graph, lang, subject):
        self.selectArgs = (graph, lang, subject)
        self.result = None
        self.hasRun = False # TODO: make configurable?


class _rdf_query_meta(type):
    def __init__(cls, clsName, bases, clsDict):
        type.__init__(cls, clsName, bases, clsDict)

        cls._selectors = selectors = {}
        for base in bases:
            if hasattr(base, '_selectors'):
                selectors.update(base._selectors)

        rdfBase = clsDict.get('_rdfbase_')
        if not rdfBase:
            for base in bases:
                if hasattr(base, '_rdfbase_'):
                    rdfBase = base._rdfbase_
                    break
        if isinstance(rdfBase, Namespace):
            cls._namespace = rdfBase
            if not clsDict.get('RDF_TYPE'):
                cls.RDF_TYPE = rdfBase[clsName]
        else:
            cls._namespace = None # TODO: pick from type?

        for key, value in clsDict.items():
            if isinstance(value, Selector):
                value.hook_into_rdf_query(key, cls)
                selectors[key] = value


class RdfQuery(object):
    __metaclass__ = _rdf_query_meta

    RDF_TYPE = RDFS.Resource

    def __init__(self, graph, lang, subject, depth=DEFAULT_MAX_DEPTH):
        # TODO: pass depth and use to avoid infinite recursion
        if depth == 0:
            raise NotImplementedError("TODO: max depth exception..")

        self._graph = graph
        self._subject = subject
        self._lang = lang
        self._preparedSelects = prepareds = {}
        for name, selector in self._selectors.items():
            if not subject: # FIXME: happens when subject is a bnode?
                setattr(self, name, None)
                continue
            prep = PreparedSelect(graph, lang, subject)
            prepareds[name] = prep

    def __str__(self):
        return str(self._subject)

    def __eq__(self, other):
        if isinstance(other, RdfQuery):
            return self._subject == other._subject
        else:
            return self._subject == other

    @property
    def uri(self):
        return self._subject

    def get_selected_value(self, name):
        return self._preparedSelects[name].result

    @classmethod
    def bound_with(cls, subject, lang=None):
        def bound_query(graph, _lang, _subject):
            return cls(graph, lang or _lang, subject)
        bound_query.query = cls
        bound_query.__name__ = cls.__name__
        return bound_query

    def to_graph(self, lgraph=None):
        subject = self._subject or BNode() # FIXME: is this ok?
        if not subject: return # FIXME, see fixme in __init__

        lgraph = lgraph or ConjunctiveGraph()

        for t in self._graph.objects(subject, RDF.type):
            lgraph.add((subject, RDF.type, t))

        for selector in self._selectors.values():
            value = selector.__get__(self)
            if not value:
                continue
            selector.back_to_graph(lgraph, subject, value)

        # FIXME: why is this happening; how can we prevent it?
        for t in lgraph:
            if None in t: lgraph.remove(t)
        return lgraph

    def to_rdf(self):
        return self.to_graph().serialize(format='pretty-xml')

    def to_dict(self, keepSubject=False):
        d = {}
        if keepSubject:
            # TODO: sync with new property 'uri'
            subjectKey = isinstance(keepSubject, str) and keepSubject or 'resource'
            subj = self._subject
            if subj and not isinstance(subj, BNode):
                d[subjectKey] = self._subject

        for selector in self._selectors.values():
            name = selector._name
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

    @classmethod
    def from_dict(cls, data, lang, subject):
        graph = ConjunctiveGraph()
        query = cls(graph, lang, subject)
        for k, v in data.items():
            setattr(query, k, v)
        return query


class Filter(object):
    def __init__(self, func):
        self.func = func
    def __call__(self, items):
        return filter(self.func, items)


class Sorter(object):
    def __init__(self, attr=None, reverse=False, ignoreCase=False):
        self.attr = attr
        self.reverse = reverse
        self.ignoreCase = ignoreCase
    def __call__(self, items):
        copy = items[:]
        copy.sort(self.sort)
        if self.reverse:
            copy.reverse()
        return copy
    def sort(self, r1, r2):
        attr = self.attr
        if attr:
            v1, v2 = getattr(r1, attr), getattr(r2, attr)
        else:
            v1, v2 = r1, r2
        if self.ignoreCase:
            v1, v2 = v1.lower(), v2.lower()
        return cmp(v1, v2)


#=======================================


# TODO: totally untested!
#def type_switch(typeSelectors, default):
#    rdfType = graph.value(resource, RDF.type, None, any=True)
#    def select(graph, lang, resource):
#        return typeSelectors.get(rdfType, default)
#    return select



def back_from_value(graph, subject, predicate, value):
        if isinstance(value, RdfQuery):
            graph.add((subject, predicate, value._subject))
            value.to_graph(graph)
        else:
            if not isinstance(value, list): # TODO: fix this
                graph.add((subject, predicate, value))


class UnarySelector(Selector):
    def back_to_graph(self, graph, subject, value):
        back_from_value(graph, subject, self.predicate, value)

class EachSelector(Selector):
    def back_to_graph(self, graph, subject, values):
        for value in values:
            back_from_value(graph, subject, self.predicate, value)


class one(UnarySelector):
    def select(self, graph, lang, subject):
        return graph.value(subject, self.predicate, None, any=True)


class each(EachSelector):
    def select(self, graph, lang, subject):
        return list(graph.objects(subject, self.predicate))


class one_where_self_is(Selector):
    def select(self, graph, lang, subject):
        return graph.value(None, self.predicate, subject, any=True)

    def back_to_graph(self, graph, subject, value):
        back_from_value(graph, value._subject, self.predicate, subject)


class each_where_self_is(Selector):
    def select(self, graph, lang, subject):
        return list(graph.subjects(self.predicate, subject))

    def back_to_graph(self, graph, subject, values):
        for value in values:
            back_from_value(graph, value._subject, self.predicate, subject)


class collection(Selector):
    def __init__(self, base, subQuery=None, multiple=False):
        Selector.__init__(self, base, subQuery)
        self.multiple = multiple

    def select(self, graph, lang, subject):
        if self.multiple:
            allItems = [graph.items(res)
                        for res in graph.objects(subject, self.predicate)]
            return list(chain(*allItems))
        else:
            return list(graph.items(
                    graph.value(subject, self.predicate, None, any=True)
                ))

    def back_to_graph(self, graph, subject, values):
        if not values:
            graph.add((subject, self.predicate, RDF.nil))
            return
        bnode = BNode()
        graph.add((subject, self.predicate, bnode))
        for value in values:
            back_from_value(graph, bnode, RDF.first, value)
            newBnode = BNode()
            graph.add((bnode, RDF.rest, newBnode))
            bnode = newBnode
        graph.add((bnode, RDF.rest, RDF.nil))


class TypeLocalized(Selector):
    def type_raw_value(self, value, lang):
        if isinstance(value, str.__base__):
            value = Literal(value, lang)
        return value

class localized(TypeLocalized, UnarySelector):
    def select(self, graph, lang, subject):
        first = None
        for value in graph.objects(subject, self.predicate):
            if not first: first = value
            if getattr(value, 'language', None) == lang:
                return value
        return first


# TODO: This is a hackish solution; see also below (transparently using datatype).
#       It also reduces the literal, making it irreversible.
from oort.util._genshifilters import language_filtered_xml
class localized_xml(UnarySelector):
    """This selector removes any elements with an xml:lang other than the 
    current language. It also supports the never standardized 'rdf-wrapper' in 
    XML Literals, who are removed from the output.

    Important! This is currently tied to the Genshi Templating System, and may 
    not work as expected in all cases."""
    def select(self, graph, lang, subject):
        return language_filtered_xml(
                graph.objects(subject, self.predicate), lang)

    def type_raw_value(self, value, lang):
        if isinstance(value, str.__base__):
            value = Literal(value, datatype=RDF.XMLLiteral)
        return value

class i18n_dict(Selector):
    def select(self, graph, lang, subject):
        valueDict = {}
        for value in graph.objects(subject, self.predicate):
            valueDict[value.language] = value
        return valueDict

    def back_to_graph(self, graph, subject, value):
        for lang, text in value.items():
            graph.add((subject, self.predicate, Literal(text, lang=lang)))


class each_localized(TypeLocalized, EachSelector):
    def select(self, graph, lang, subject):
        return [ value for value in graph.objects(subject, self.predicate)
                 if value.language == lang ]


#=======================================


class selector(Selector):
    "Use as decorator for methods of an RdfQuery subclass to convert them to selectors."
    def __init__(self, func):
        super(selector, self).__init__(None)
        self.func = func
    def retreive_result(self, parentQuery, selectArgs):
        return self.func(parentQuery, *selectArgs)


#=======================================
# TODO: consider returning ElementTree data for XML Literals. And if so, also
# filtered on u'{http://www.w3.org/XML/1998/namespace}lang' (keep if none) for localized.

# TODO: also consider checking datatype and coercing (at least) these:
# Use: rdflib.Literal.castPythonToLiteral
# See: rdflib.sparql.sparqlOperators.getLiteralValue(v)
# See: <http://en.wikipedia.org/wiki/RDFLib#RDF_Literal_Support>


#=======================================

def chain(*iters):
    for iterator in iters:
        for i in iterator: yield i


