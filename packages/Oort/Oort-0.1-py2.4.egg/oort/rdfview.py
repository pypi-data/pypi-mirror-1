#=======================================================================
import rdflib
from rdflib import RDF, Namespace, Graph, BNode
try: import simplejson
except ImportError: simplejson = None
#=======================================================================
# TODO: remove SCHEMA unless a proper use is implemented!


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


class _rdf_query_meta(type):
    def __new__(cls, clsName, bases, clsDict):
        SCHEMA = clsDict.get('SCHEMA')
        if not SCHEMA:
            for base in bases:
                if hasattr(base, 'SCHEMA'): SCHEMA = base.SCHEMA; break
        # TODO: consider opt. SCHEMA and/or type as a resource filter (thus not
        # querying more if resource is not of the given type)
        selectors = clsDict['_selectors'] = {}
        for base in bases:
            if hasattr(base, '_selectors'):
                selectors.update(base._selectors)
        for key, value in clsDict.items():
            if callable(value) and getattr(value, 'selectorMaker', False):
                selectors[key] = value(key)
                del clsDict[key] # TODO: or not?
        return type.__new__(cls, clsName, bases, clsDict)


class RdfQuery(object):
    __metaclass__ = _rdf_query_meta

    SCHEMA = None

    def __init__(self, graph, subject, lang, depth=DEFAULT_MAX_DEPTH):
        self._graph = graph
        self._subject = subject
        self._lang = lang
        if depth > 0:
            # TODO: pass depth and use..
            for name, selector in self._selectors.items():
                if subject is None: # FIXME: proably when subject is a bnode..
                    setattr(self, name, None)
                    continue
                setattr(self, name, selector(self, graph, subject, lang))

    def __str__(self):
        return str(self._subject)

    _reversables = {}

    @classmethod
    def graph_reversable(cls, *selectorNames):
        def decorator(func):
            for name in selectorNames:
                cls._reversables[name] = func
            return func
        return decorator

    def to_graph(self, lgraph=None):
        subject = self._subject or BNode() # FIXME: is this ok?
        if not subject: return # FIXME, see fixme in __init__

        lgraph = lgraph or Graph()

        for t in self._graph.objects(subject, RDF.type):
            lgraph.add((subject, RDF.type, t))

        for name, selector in self._selectors.items():
            predicate = getattr(selector, 'forPredicate', None)
            if not predicate:
                continue
            value = getattr(self, name)
            reversor = self._reversables.get(selector.func_name)
            if reversor:
                reversor(lgraph, subject, predicate, value)

        # FIXME: why is this happening; how can we prevent it?
        for t in lgraph:
            if None in t: lgraph.remove(t)
        return lgraph

    def to_rdf(self):
        return self.to_graph().serialize(format='pretty-xml')

    def to_dict(self, keepSubject=False):
        d = {}
        if keepSubject:
            subjectKey = isinstance(keepSubject, str) and keepSubject or '_rdf_about'
            subj = self._subject
            if subj and not isinstance(subj, BNode):
                d[subjectKey] = self._subject
        for name in self._selectors:
            value = getattr(self, name)
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
# TODO: expose *_query functions as stand-alone selector helpers(?)


# TODO:
#class Selector(object):
#   __slots__ = ()
#    def __rshift__(self, aspect):
#        self.aspect = aspect
#        return self
#    def __or__(self, sorter):
#        self.sorter = sorter
#        return self



def _get_pred(nsOrResource, propName):
    # TODO: enough if getitem or getattr returns URIRef..
    if isinstance(nsOrResource, Namespace):
        return nsOrResource[propName]
    else:
        return nsOrResource

def joined_iters(*iters):
    for iter in iters:
        for i in iter: yield i

def type_switch(typeSelectors, default):
    rdfType = graph.value(resource, RDF.type, None, any=True)
    def select(graph, resource, lang):
        return typeSelectors.get(rdfType, default)
    return select


# TODO: if no rdfQuery selector, let metaclass infer from rdf:type to use 
# RdfQuery subclass? Needs to register all RdfQuery instances? Some?
# or keep (after testing!) type_switch?
def _query_resources(resources, currQueryObj, rdfQuery, graph, lang):
    if not resources:
        return ()
    if not rdfQuery:
        return resources
    if rdfQuery is THIS_QUERY:
        #raise Warning(
        #        'Using THIS_QUERY may currently cause infinite loops.') # FIXME
        rdfQuery = type(currQueryObj)
    return [rdfQuery(graph, uri, lang) for uri in resources]


def one(nsOrResource, rdfQuery=None):
    def mk_one_query(propName):
        pred = _get_pred(nsOrResource, propName)
        def one_query(self, graph, subj, lang):
            res = _query_resources([graph.value(subj, pred, None, any=True)],
                    self, rdfQuery, graph, lang)
            return res and res[0] or None
        one_query.forPredicate = pred
        return one_query
    mk_one_query.selectorMaker = True
    return mk_one_query

def localized(nsOrResource):
    def mk_localized_query(propName):
        pred = _get_pred(nsOrResource, propName)
        def localized_query(self, graph, subj, lang):
            first = None
            for value in graph.objects(subj, pred):
                if not first: first = value
                if getattr(value, 'language', None) == lang:
                    return value
            return first
        localized_query.forPredicate = pred
        return localized_query
    mk_localized_query.selectorMaker = True
    return mk_localized_query

# TODO: this is a somewhat dirty solution; see also below (transparently using datatype)
from oort.etreeutil import language_filtered_xml
def localized_xml(nsOrResource):
    def mk_localized_xml_query(propName):
        pred = _get_pred(nsOrResource, propName)
        def localized_xml_query(self, graph, subj, lang):
            return language_filtered_xml(graph.objects(subj, pred), lang)
        localized_xml_query.forPredicate = pred
        return localized_xml_query
    mk_localized_xml_query.selectorMaker = True
    return mk_localized_xml_query

@RdfQuery.graph_reversable('one_query', 'localized_query', 'localized_xml_query')
def back_from_value(graph, subject, predicate, value):
    if isinstance(value, RdfQuery):
        graph.add((subject, predicate, value._subject))
        value.to_graph(graph)
    else:
        if not isinstance(value, list): # TODO: fix this
            graph.add((subject, predicate, value))


def i18n_dict(nsOrResource):
    def mk_i18n_query(propName):
        pred = _get_pred(nsOrResource, propName)
        def i18n_query(self, graph, subj, lang):
            valueDict = {}
            for value in graph.objects(subj, pred):
                valueDict[value.language] = value
            return valueDict
        i18n_query.forPredicate = pred
        return i18n_query
    mk_i18n_query.selectorMaker = True
    return mk_i18n_query

# FIXME: graph_reversable for i18n_dict


def each(nsOrResource, rdfQuery=None):
    def mk_each_query(propName):
        pred = _get_pred(nsOrResource, propName)
        def each_query(self, graph, subj, lang):
            return _query_resources(graph.objects(subj, pred),
                    self, rdfQuery, graph, lang)
        each_query.forPredicate = pred
        return each_query
    mk_each_query.selectorMaker = True
    return mk_each_query

def each_localized(nsOrResource):
    def mk_each_localized_query(propName):
        pred = _get_pred(nsOrResource, propName)
        def each_localized_query(self, graph, subj, lang):
            for value in graph.objects(subj, pred):
                if value.language == lang:
                    yield value
        each_localized_query.forPredicate = pred
        return each_localized_query
    mk_each_localized_query.selectorMaker = True
    return mk_each_localized_query

@RdfQuery.graph_reversable('each_query', 'each_localized_query')
def back_from_each(graph, subject, predicate, values):
    for value in values:
        back_from_value(graph, subject, predicate, value)


def collection(nsOrResource, rdfQuery=None, multiple=False):
    def mk_collection_query(propName):
        pred = _get_pred(nsOrResource, propName)
        def collection_query(self, graph, subj, lang):
            if multiple:
                allItems = [graph.items(res) for res in graph.objects(subj, pred)]
                items = joined_iters(*allItems)
            else:
                items = graph.items(graph.value(subj, pred, None, any=True))
            return _query_resources(items, self, rdfQuery, graph, lang)
        collection_query.forPredicate = pred
        return collection_query
    mk_collection_query.selectorMaker = True
    return mk_collection_query

@RdfQuery.graph_reversable('collection_query')
def back_from_collection(graph, subject, predicate, values):
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


def selector(func):
    "Use as decorator for methods of an RdfQuery subclass to convert them to selectors."
    def mk_selector(propName):
        return func
    mk_selector.selectorMaker = True
    return mk_selector


# EOF
