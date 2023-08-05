from rdflib import *
from oort.rdfview import *


T = Namespace("http://example.org/oort/test#")

class Part(RdfQuery):
    name = one(T)

class Item(Part):
    title = localized(T)
    relations = each(T.relation) >> THIS_QUERY
    collection = collection(T) >> Part
    xmlData = localized_xml(T)
    titleLang = i18n_dict(T['title'])
    labels = each_localized(T.label)

class RichItem(Item):
    xmlData = localized_xml(T)

class CustomItem(Item):
    @selector
    def randomRelation(self, graph, lang, subject, predicate):
        from random import randint
        assert isinstance(self, CustomItem)
        itemUris = [uri for uri in graph.subjects(RDF.type, T.Item)
                        if uri != subject]
        return Part(graph, lang, itemUris[randint(0, len(itemUris)-1)])


#=======================================


import os
TEST_DATA = os.path.join(os.path.dirname(__file__), 'testdata.n3')
graph = rdflib.Graph()
graph.load(open(TEST_DATA), format='n3')

itemX = URIRef('urn:test:item:x')
en, sv = 'en', 'sv'

def test_one():
    assert Item(graph, en, itemX).name == u'Item X'

def test_each():
    relItemNames = [item.name for item in Item(graph, en, itemX).relations]
    assert set(relItemNames) == set(["Related 1", "Related 2"])

def test_collection():
    collItems = [item.name for item in Item(graph, en, itemX).collection]
    assert set(collItems) == set(["Part 1", "Part 2"])

def assertEquals(v1, v2): assert v1 == v2

def test_localized():
    for l, v in [(en, u'Example Item'), (sv, u'Exempelsak')]:
        yield assertEquals, Item(graph, l, itemX).title, v

def test_localized_xml():
    for l, v in [(en, u'XML Data'), (sv, u'XML-data')]:
        treeData = list(RichItem(graph, l, itemX).xmlData)
        ok = False
        for stream in treeData:
            for item in stream:
                if v in item: ok = True
        assert ok

def test_i18n_dict():
    titleLangs = Item(graph, en, itemX).titleLang
    assert set(titleLangs.keys()) == set(['en', 'sv'])
    assert set(titleLangs.values()) == set([u'Example Item', u'Exempelsak'])

def test_each_localized():
    assert set(Item(graph, en, itemX).labels) == set([u'En', u'eN'])
    assert set(Item(graph, sv, itemX).labels) == set([u'Sv', u'sV'])


def test_to_json():
    json = Item(graph, en, itemX).to_json()
    # TODO: parse and inspect!


def test_selector_decorator():
    assert CustomItem(graph, en, itemX).randomRelation.name.startswith("Related ")


