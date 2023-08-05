#=======================================================================
import os
from os.path import splitext, expanduser
from rdflib import Namespace
#=======================================================================
# TODO: (optional?) poorMansInference!
#           - interpret rdfs (also using equiv. owl terms)
#           - optional vocabulary discovery?


OUG_NS = Namespace('tag:oort.to,2006:system/util/graphs#')
LAST_MOD = OUG_NS.lastmodified

def load_if_modified(graph, fpath, format):
    dataUri = graph.absolutize(fpath)
    modTime = os.stat(fpath).st_mtime
    try:
        loadedModValue = graph.value(dataUri, LAST_MOD)
        loadedModTime = int(loadedModValue)
    except TypeError:
        loadedModTime = -1
    if modTime > loadedModTime:
        graph.remove((dataUri, LAST_MOD, loadedModValue))
        graph.remove_context(graph.context_id(dataUri))
        print "Loading: %s" % dataUri
        graph.load(fpath, publicID=dataUri, format=format)
        graph.add((dataUri, LAST_MOD, modTime))


DEFAULT_FORMAT_MAP = {
        # TODO: rdf/a
        'rdf': 'xml',
        'n3':'n3',
    }

def get_format(fpath, fmap=None):
    fmap = fmap or DEFAULT_FORMAT_MAP
    ext = splitext(fpath)[-1][1:]
    return fmap.get(ext)


def loader(graph, base=None, formatMap=None):
    if base: base = expanduser(base) + '%s'
    def load_data(fpath):
        if base:
            fpath = base % fpath
        load_if_modified(graph, fpath, format=get_format(fpath, formatMap))
    return load_data


def load_dir(graph, basedir, formatMap=None, errorHandler=None):
    basedir = expanduser(basedir)
    for base, fdirs, fnames in os.walk(basedir):
        for fname in fnames:
            fpath = os.path.join(base, fname)
            format = get_format(fpath, formatMap)
            if not format:
                continue
            try:
                load_if_modified(graph, fpath, format)
            except Exception, e:
                if errorHandler:
                    errorHandler(e, fpath)
                else:
                    raise e


