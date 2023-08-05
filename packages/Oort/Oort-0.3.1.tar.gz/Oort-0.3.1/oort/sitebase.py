# -*- coding: UTF-8 -*-
# FIXME: really, fix the "variant" concept..
# TODO: option to give ignored suffix for e.g. downloading..?
# TODO: Work on SubTypeAwareDisplay (partially done; consider using "poorMansInference")
#   - or <http://dev.w3.org/cvsweb/~checkout~/2004/PythonLib-IH/RDFSClosure.py>
"""
"""
#=======================================================================
import urllib
from pkg_resources import EntryPoint
from rdflib import URIRef
from paste.wsgiwrappers import WSGIRequest, WSGIResponse
from paste.httpexceptions import HTTPTemporaryRedirect
from oort.display import DisplayBase, Display, SubTypeAwareDisplay
from oort.display import AspectBase, Aspect, TpltAspect, JsonAspect, RdfAspect
from oort.rdfview import RdfQuery
from oort.util.code import SlotStruct, contract, autosuper
__metaclass__ = autosuper
#=======================================================================


class resource_viewer_meta(autosuper):
    def __init__(cls, clsName, bases, clsDict):
        autosuper.__init__(cls, clsName, bases, clsDict)
        displays = clsDict.setdefault('displays', {})
        defaultDisplay = clsDict.get('defaultDisplay')
        for member in clsDict.values():
            if isinstance(member, type) and issubclass(member, DisplayBase):
                name = getattr(member, 'name', None)
                if not name:
                    continue
                displays[name] = member()
                if not defaultDisplay and getattr(member, 'default', False):
                    defaultDisplay = name
        cls.displays = displays
        cls.defaultDisplay = defaultDisplay


class ResourceViewerBase:
    __metaclass__ = resource_viewer_meta

    @classmethod
    def app_factory(cls, global_conf=None,
                    graph_factory=None, debug='False', **kwargs):
        mk_graph = EntryPoint.parse("x=%s" % graph_factory).load(False)
        graph = mk_graph()
        debug = debug.capitalize() == str(True)
        return cls(graph, debug)

    VARIANT_SEP = '-'
    RESOURCE_QUERY_KEY = 'resource'

    #displays = {}
    #defaultDisplay = None
    langOrder = ()

    def __init__(self, graph, debug=False):
        self.graph = graph
        self._debug = debug

    def __call__(self, environ, start_response):
        req = WSGIRequest(environ)

        self._viewPathTemplate = req.script_name + '/%s/%s/'
        args = req.path_info.split('/')
        try:
            args.pop(0) # remove first ''
            lang = args.pop(0)
            displayArg = args.pop(0)
        except IndexError:
            lang, displayArg = None, None
        if not displayArg:
            return self._default_redirect(lang, environ, start_response)

        uri = req.GET.get(self.RESOURCE_QUERY_KEY) or self.resource_from(args)

        get_result, contentType = self.prepared_display(
                URIRef(uri), lang, displayArg, req)

        headerMap = {}
        if contentType:
            headerMap['Content-Type'] = contentType

        start_response('200 OK', headerMap.items())
        return get_result(self.graph)

    def _default_redirect(self, lang, environ, start_response):
        redirect = HTTPTemporaryRedirect(
                self.app_url_for(lang or self.langOrder[0], self.defaultDisplay))
        return redirect(environ, start_response)

    @contract.template_method
    def resource_from(self, pathArgs):
        raise NotImplementedError

    @contract.template_method
    def resource_to_app_path(self, resource):
        raise NotImplementedError

    def app_url_for(self, lang, displayArg, resource=None):
        urlBase = self._viewPathTemplate % (lang, displayArg)
        if resource:
            resource, success = self.resource_to_app_path(resource)
            if success:
                return urlBase + resource.replace('#', '%23')
            else:
                return '%s?%s=%s' % (urlBase, self.RESOURCE_QUERY_KEY,
                                     urllib.quote(resource))
        else:
            return urlBase

    def prepared_display(self, resource, lang, displayArg, req):
        args = displayArg.split(self.VARIANT_SEP, 1)
        name, variantArg = args[0], len(args) > 1 and args[1]
        display = self.displays[name]
        current = Current(resource, lang)
        appUtil = AppUtil(current, displayArg, self, req)

        if self._debug:
            print "DEBUG:", current, appUtil, display # TODO: use __repr__ and logging

        def get_result(graph):
            return display.get_result_generator(graph, appUtil, variantArg)

        return get_result, display.contentType


class Current(SlotStruct):
    __slots__ = 'resource', 'lang'

class AppUtil(SlotStruct):
    """"An instance of this class is provided to the templates under the name 
    'app'. It provides a controlled interface to the application and the 
    current state (request)."""

    __slots__ = 'current', '_displayArg', '_view', '_req'

    def queries(self, queries):
        for query in queries:
            yield query(self._view.graph, self.current.resource, self.current.lang)

    def link(self, resource=None, lang=None, display=None, displayArg=None):
        """Returns an URL within the current app. The following arguments 
        can be given (all defaults to current unless provided):

            resource
                a target URI or an instance of an RdfQuery

            lang
                the language to use

            display
                the display name to use
        """
        if resource:
            if isinstance(resource, RdfQuery):
                resource = resource._subject
        else: resource = self.current.resource
        lang = lang or self.current.lang
        displayArg = display or displayArg or self._displayArg
        return self._view.app_url_for(lang, displayArg, resource)

    @property
    def baseurl(self):
        """Returns the base URL of this web app."""
        return self._req.script_name


class ResourceViewer(ResourceViewerBase):
    resourceBase =None
    trailSep='/'

    def __init__(self, *args):
        self.__super.__init__(*args)
        self._uriBase = self.resourceBase + "%s"

    def resource_from(self, pathArgs):
        return self._uriBase % self.trailSep.join(pathArgs)

    def resource_to_app_path(self, resource):
        base = self.resourceBase
        if resource.find(base) == 0:
            return str(resource)[len(base):], True
        else:
            return resource, False


class MultiBaseResourceViewer(ResourceViewerBase):
    resourceBases = {}
    defaultResource = ''
    # TODO: skip defaultResource and use defaultResourceBase?
    # TODO: if bad baseKey, raise Exception instead?

    def resource_from(self, pathArgs):
        if not pathArgs:
            return self.defaultResource
        pathArgs = list(pathArgs)
        baseKey = pathArgs.pop(0)
        lookup = self.resourceBases.get(baseKey)
        if not lookup:
            return self.defaultResource
        uriBase, trailSep = lookup
        return uriBase + trailSep.join(pathArgs)

    def resource_to_app_path(self, resource):
        for baseKey, (base, trailSep) in self.resourceBases.items():
            if resource.find(base) == 0:
                respath = str(resource)[len(base):]
                if trailSep:
                    respath = respath.replace(trailSep, '/')
                lpath = "%s/%s" % (baseKey, respath)
                return lpath, True
        return resource, False


