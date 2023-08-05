#=======================================================================
import rdflib
from rdflib import RDF, RDFS
from oort.rdfview import *
#=======================================================================


DC = Namespace("http://purl.org/dc/elements/1.1/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
TIME = Namespace("http://pervasive.semanticweb.org/ont/2004/06/time#")
T = Namespace("http://example.org/oort/test#")


class Person(RdfQuery):
    label = localized (RDFS.RDFSNS)
    comment = localized (RDFS.RDFSNS)
    name = one (FOAF)
    bday = one (FOAF)
    title = localized (DC)
    @property
    def combinedLabel(self):
        return "%s (%s)" % (self.name, self.title)


class Described(RdfQuery):
    value = localized (RDF.RDFNS)
    label = localized (RDFS.RDFSNS)
    comment = localized (RDFS.RDFSNS)

class DescribedAndDescribedType(Described):
    type = one (RDF.RDFNS) >> Described

class TimeEvent(RdfQuery):
    startDate = one(TIME['from'])
    endDate = one(TIME.to)

class DescribedTimeEvent(Described, TimeEvent):
    pass


class BasicProps(RdfQuery):
    pass # TODO


class Skill(RdfQuery):
    what = one(T['in']) >> DescribedAndDescribedType

class Organization(Described):
    pass

class Project(Described):
    contractor = one(T) >> Organization

class ProjectContribution(DescribedTimeEvent):
    forProject = one(T) >> Project
    usedTechnologies = collection(T) >> BasicProps

class CourseEvent(BasicProps, DescribedTimeEvent):
    pass

class Interest(Described):
    technologies = collection(T) >> BasicProps

class Consultant(Person):

    mainInterests = collection(T) >> Interest
    skills = each(T.skill) >> Skill
    spokenLanguages = each(T.speaksLanguage) >> BasicProps

    # TODO: choice is not implemented!
    #involvedIn = each(T) >> choice(ProjectContribution, CourseEvent) | 'date'
    #
    #involvedIn = each(T) >> choice(ProjectContribution, CourseEvent) \
    #        | (lambda one, other: cmp(one.date, other.date))

    # TODO: groups is not implemented! .. as dict or obj with attributes? Both?
    #involvements = each(T.involvedIn) >> groups(projects=ProjectContribution,
    #                                           courses=CourseEvent)

    attendedAt = each(T, CourseEvent)



class MainResources(RdfQuery):
    def __init__(self, *args, **kwargs):
        self._skills = None
        self._categories = None
        RdfQuery.__init__(self, *args, **kwargs)

    # TODO: persons = subjects(RDF.type, T.Consultant) >> PersonBase
    @selector
    def persons(self, graph, _res, lang):
        return [PersonBase(graph, subj, lang) for subj
                in graph.subjects(RDF.type, T.Consultant)]

    @selector
    def skills(self, graph, resource, lang):
        if not self._skills:
            self._skills = [BasicAndDescribedType(graph, subj, lang)
                    for subj in graph.objects(None, T['in'])]
        return self._skills

    @selector
    def categories(self, graph, resource, lang):
        if not self._categories:
            collected = set()
            categories = set()
            for skill in self._skills:
                subj = skill.type._subject
                if subj and subj not in collected:
                    collected.add(subj)
                    categories.add(skill.type)
            self._categories = categories
        return self._categories


#=======================================================================


class TestRdfView:

    def test_stuff(self):
        pass


