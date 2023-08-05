#=======================================================================
from rdflib import Graph, Namespace, URIRef, RDF, RDFS
from oort.display import SubTypeAwareDisplay
#=======================================================================

ont = Namespace("urn:ont#")

class TestSubTypeAwareDisplay:

    def setup(self):
        typeAspects = {ont.T1: "T1 handler", ont.T5: "T5 handler"}
        #typeAspects = {ont.T2: "handler for T2", ont.T3: "handler for T3"}
        self.display = SubTypeAwareDisplay()
        self.display.typeAspects = typeAspects

    def test_create_match_graph(self):
        # TODO: verify test accuracy; then remake into test generator (see nose)

        graph = Graph()

        def classAndSubClass(C1, C2):
            graph.add( (C1, RDF.type, RDFS.Class) )
            graph.add( (C2, RDF.type, RDFS.Class) )
            graph.add( (C2, RDFS.subClassOf, C1) )

        classAndSubClass(ont.T1, ont.T2)
        classAndSubClass(ont.T2, ont.T3)
        classAndSubClass(ont.T3, ont.T4)
        classAndSubClass(ont.T4, ont.T5)

        item1 = URIRef("urn:item1")
        item2 = URIRef("urn:item2")
        item3 = URIRef("urn:item3")
        item4 = URIRef("urn:item4")
        item5 = URIRef("urn:item5")

        graph.add( (item1, RDF.type, ont.T1) )
        graph.add( (item2, RDF.type, ont.T2) )
        graph.add( (item3, RDF.type, ont.T3) )
        graph.add( (item4, RDF.type, ont.T4) )
        graph.add( (item5, RDF.type, ont.T5) )

        matchGraph = self.display.create_match_graph(graph)

        def get_aspect(resource):
            for rdfType in matchGraph.objects(resource, RDF.type):
                return self.display.typeAspects.get(rdfType)

        assert get_aspect(item1) == "T1 handler"
        assert get_aspect(item2) == "T1 handler"
        assert get_aspect(item3) == "T1 handler"
        assert get_aspect(item4) == "T1 handler"
        assert get_aspect(item5) == "T5 handler"


