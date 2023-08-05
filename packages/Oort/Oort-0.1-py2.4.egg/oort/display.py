# -*- coding: UTF-8 -*-
# TODO: use Buffet-style templating instead (and provide way to serialize RdfQuery:s)
#=======================================================================
import os.path
from rdflib import RDF, RDFS, Graph
import kid
from oort.util import templating
from oort.util.code import contract, autosuper
__metaclass__ = autosuper
#=======================================================================

class DisplayBase:

    contentType = None

    @contract.template_method
    def get_result_generator(self, graph, appUtil, variantArg):
        raise NotImplementedError


class Display(DisplayBase):

    # TODO: for outputEncoding, see Aspect problems below.
    #       May need to redesign to set template-speficic stuff instead.
    #       These options should be available as data too (e.g. for template
    #       output and/or encoding specific stuff..).
    outputMethod = None
    outputEncoding  = None

    templateBase = ""
    globalQueries = None
    aspects = []

    def __init__(self):
        self.typeAspects = {}
        self.variantAspects = {}
        for aspect in self.aspects:
            aspect.initialize(self.templateBase, self.globalQueries)
            if aspect.forVariant:
                variant = self.variantAspects.setdefault(aspect.forVariant, {})
                typeDict = variant
            else:
                typeDict = self.typeAspects
            typeDict[aspect.forType] = aspect

    @contract.default_method
    def parse_variant(self, variantStr):
        return variantStr

    def get_result_generator(self, graph, appUtil, variantArg):
        variant = self.parse_variant(variantArg)
        data = self.get_extra_data(appUtil, variant) or {}
        data['app'] = appUtil
        resource, lang = appUtil.current.resource, appUtil.current.lang
        aspect = self.get_aspect(graph, resource, variant)
        generate = aspect.make_result_generator(graph, resource, lang, data)
        return generate(encoding=self.outputEncoding, output=self.outputMethod)

    def get_aspect(self, graph, resource, variant):
        rdfType = RDFS.Resource
        for _type in graph.objects(resource, RDF.type):
            rdfType = _type; break
        typeDict = self.typeAspects
        if variant:
            typeDict = self.variantAspects.get(variant) or self.typeAspects
        return typeDict.get(rdfType) or typeDict[RDFS.Resource]

    @contract.default_method
    def get_extra_data(self, appUtil, variant):
        "Use for further template preparation based on current request."
        return None


class KeywordVariantParser:
    pass # TODO


class SubTypeAwareDisplay(Display):

    def __init__(self):
        self.__super.__init__()
        self._matchGraph = None

    def get_aspect(self, graph, resource, variant):
        if not self._matchGraph:
            self._matchGraph = self.create_match_graph(graph)
        return self.__super.get_aspect(self._matchGraph, resource, variant)

    def create_match_graph(self, graph):
        """For optimization, creating a sparse graph of "best matching"
        for all resources and querying only that at runtime. """
        typeAspects = self.typeAspects
        def list_with_sub_types(rdfType):
            yield rdfType
            for subType in graph.subjects(RDFS.subClassOf, rdfType):
                if subType not in typeAspects:
                    for subSub in list_with_sub_types(subType):
                        yield subSub

        sparseGraph = Graph()
        for handledType in typeAspects:
            for anySub in list_with_sub_types(handledType):
                for resource in graph.subjects(RDF.type, anySub):
                    sparseGraph.add((resource, RDF.type, handledType))

        return sparseGraph

    # TODO: Implement? Not really useful if create_match_graph is used;
    # however, this one is *much* better if resources are volatile..
    #def get_aspect(resource):
    #    for rType in graph.objects(resource, RDF.type):
    #        if rType in _mostSpecificHandled:
    #            return typeAspects.get(rType)
    #        supType = _handledSupers.get(rType)
    #        if supType:
    #            return typeAspects.get(supType)
    #    return typeDict[RDFS.Resource]


class AspectBase:

    def __init__(self, forType, templateName, queries=None, forVariant=None):
        self.forType = forType
        self.templateBase = None
        self.templateName = templateName
        self.queries = queries or ()
        self.forVariant = forVariant

    @contract.state_change
    def initialize(self, templateBase, globalQueries):
        self.templateBase = templateBase
        if globalQueries:
            queries = globalQueries.copy()
            queries.update(self.queries)
            self.queries = queries

    @contract.helper
    def generate_query_items(self, graph, resource, lang):
        """Generates key, value pairs which constitute named, run queries."""
        if self.queries:
            for name, query in self.queries.items():
                yield name, query(graph, resource, lang)

    # TODO: redesign contract to set encoding and output(method) on call to Aspect#initialize?
    @contract.template_method
    def make_result_generator(self, graph, resource, lang, data=None):
        """
        Returns a generator that takes the arguments 'encoding' and 'output'.
        """
        raise NotImplementedError


class Aspect(AspectBase):

    def initialize(self, base, globalQueries):
        self.__super.initialize(base, globalQueries)
        self.template = kid.load_template(
                os.path.join(base, self.templateName), cache=True)

    def make_result_generator(self, graph, resource, lang, data=None):
        tplt = self.template.Template()
        for name, result in self.generate_query_items(graph, resource, lang):
            setattr(tplt, name, result)
        data and [setattr(tplt, name, value)
                        for name, value in data.items()]
        return tplt.generate


class TpltAspect(AspectBase):

    engineManager = templating.TemplateEngineManager(None, {})

    defaultEngine = "kid"

    def initialize(self, base, globalQueries):
        self.__super.initialize(None, globalQueries)
        self.engine, self.path = self.engineManager.get_engine_and_path(
                base+'.'+self.templateName, self.defaultEngine)
        template = self.engine.load_template(self.path)
        self.template = template or None

    def make_result_generator(self, graph, resource, lang, data=None):
        allData = dict(self.generate_query_items(graph, resource, lang))
        if data:
            allData.update(data)
        engine = self.engine
        template = self.template or self.path
        # FIXME: needs to use encoding, but alas, the plugin format precludes it...
        def generator(encoding, output):
            result = engine.render(allData, format=output, template=template)
            yield result
        return generator


class JsonAspect(AspectBase):

    def __init__(self, forType, queries, subjectKey=False):
        self.__super.__init__(forType, None, queries)
        self.subjectKey = subjectKey

    def make_result_generator(self, graph, resource, lang, data=None):
        qData = dict( self.generate_query_items(graph, resource, lang) )
        def generator(encoding, output):
            # TODO: use encoding!
            yield '{'
            for i, (key, result) in enumerate(qData.items()):
                if i != 0: yield ","
                yield "'%s':" % key
                yield result.to_json(self.subjectKey)
            yield '}'
        return generator


