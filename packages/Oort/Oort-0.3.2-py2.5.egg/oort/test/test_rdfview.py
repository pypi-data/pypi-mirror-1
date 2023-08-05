from rdflib import ConjunctiveGraph, URIRef
from oort.rdfview import *
from oort.test import mergepaths

# TODO: test some with rdflib.RDFS to make sure module namespaces work.

T = Namespace("http://example.org/oort/test#")

class Part(RdfQuery):
    name = one(T)

class Item(Part):
    title = localized(T)
    relations = each(T.relation) >> THIS_QUERY
    unaryRelation = one(T) >> Part
    collection = collection(T) >> Part
    xmlData = localized_xml(T)
    titleLang = i18n_dict(T['title'])
    labels = each_localized(T.label)


def assert_contains(graph, query):
    for spo in query.to_graph():
        assert spo in graph


#=======================================


TEST_DATA = mergepaths(__file__, 'testdata.n3')
graph = ConjunctiveGraph()
graph.load(open(TEST_DATA), format='n3')

itemX = URIRef('tag:oort.to,2006:test:item:x')
en, sv = 'en', 'sv'

def test_one():
    assert Item(graph, en, itemX).name == u'Item X'

def test_one_relation():
    assert Item(graph, en, itemX).unaryRelation.name == u'One Relation'

def test_each():
    relItemNames = [item.name for item in Item(graph, en, itemX).relations]
    assert set(relItemNames) == set(["Related 1", "Related 2"])

def test_collection():
    collItems = [item.name for item in Item(graph, en, itemX).collection]
    assert set(collItems) == set(["Part 1", "Part 2"])

def assert_equals(v1, v2): assert v1 == v2

def test_localized():
    for l, v in [(en, u'Example Item'), (sv, u'Exempelsak')]:
        yield assert_equals, Item(graph, l, itemX).title, v

class RichItem(Item):
    xmlData = localized_xml(T)

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


class Creation(RdfQuery):
    createdBy = one_where_self_is(T.creation) >> Part

def test_one_where_self_is():
    creation = Creation(graph, en, itemX)
    assert creation.createdBy.name == "Creator"
    assert_contains(graph, creation)


class Owner(RdfQuery):
    owns = each_where_self_is(T.owner) >> Part

def test_each_where_self_is():
    owner = Owner(graph, en, itemX)
    owned = [part.name for part in owner.owns]
    assert set(owned) == set(["Part A", "Part B"])
    assert_contains(graph, owner)


def test_to_json():
    json = Item(graph, en, itemX).to_json()
    d = eval(json)
    # TODO: inspect!


def test_to_graph():
    itemGraph = Item(graph, en, itemX).to_graph()
    # TODO: inspect!


class CustomItem(Item):
    @selector
    def randomRelation(self, graph, lang, subject):
        from random import randint
        assert isinstance(self, CustomItem)
        itemUris = [uri for uri in graph.subjects(RDF.type, T.Item)
                        if uri != subject]
        return Part(graph, lang, itemUris[randint(0, len(itemUris)-1)])

def test_selector_decorator():
    assert CustomItem(graph, en, itemX).randomRelation.name.startswith("Related ")


class FilteredItem(RdfQuery):
    sortedKeywords = each(T.keyword) | Sorter()
    sortedKeywordsReversed = each(T.keyword) | Sorter(reverse=True)
    someKeywords = each(T.keyword) | Filter(lambda v: v in ('q', 'r', 'y'))
    name_upper = one(T.name) | (lambda v: unicode(v).upper())

def test_filter():
    item = FilteredItem(graph, en, itemX)

    yield assert_equals, item.name_upper, "ITEM X"

    def assert_sorted(item):
        keywords = "e q r t w y".split()
        assert item.sortedKeywords == keywords
        keywords.reverse()
        assert item.sortedKeywordsReversed == keywords

    yield assert_sorted, item

    def assert_some(item):
        assert set(item.someKeywords) == set(['q', 'r', 'y'])

    yield assert_some, item


class ImplicitItem(RdfQuery):
    _rdfbase_ = T
    name = one()

def test_implicit_item():
    item = ImplicitItem(graph, en, itemX)
    assert item.name == "Item X"
    assert ImplicitItem.RDF_TYPE == T.ImplicitItem

class TypedImplicitItem(RdfQuery):
    _rdfbase_ = T
    RDF_TYPE = T.OtherType
    name = one()

def test_typed_implicit_item():
    item = TypedImplicitItem(graph, en, itemX)
    assert item.name == "Item X"
    assert TypedImplicitItem._rdfbase_ == T
    assert TypedImplicitItem.RDF_TYPE == T.OtherType


def test_from_dict():
    data = dict(
        name = "Item X",
        title = "Example Item",
        titleLang = { 'en': "Example Item", 'sv': "Exempelsak" },
        labels = [ "En", "eN" ],
        relations = [
                {'name': "Related 1"},
                {'name': "Related 2"},
            ],
        xmlData = "<div/>",
    )
    item = Item.from_dict(data, "en", URIRef("tag:oort.to,2006/test/item/x_fromdict"))
    # TODO: verify graph!
    item.to_graph()
    #print item.to_rdf(); raise Exception


def test_bound_with():
    bound = Item.bound_with(itemX)
    yield assert_equals, bound.query, Item
    yield assert_equals, bound.__name__, 'Item'
    yield assert_equals, bound(graph, en, BNode()).name,  u'Item X'
    bound = Item.bound_with(itemX, sv)
    yield assert_equals, bound(graph, en, BNode()).title, u'Exempelsak'


