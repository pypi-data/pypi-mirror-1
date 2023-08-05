import os
from os.path import basename, splitext, expanduser
from rdflib import URIRef

# TODO: define better namespace (oort? fodder?)
# TODO: (optional?) poorMansInference!
#           - interpret rdfs (also using equiv. owl terms)
#           - optional vocabulary discovery?

LAST_MOD = URIRef('urn:filesystem:lastmodified')

def loader(graph, base=None):
    if base: base = expanduser(base) + '%s'

    def load_data(fname):
        if base: fname = base % fname
        kwargs = {}
        if splitext(basename(fname))[-1] == '.n3':
            kwargs['format'] = 'n3'
        dataUri = graph.absolutize(fname)
        modTime = os.stat(fname).st_mtime
        try:
            loadedModValue = graph.value(dataUri, LAST_MOD)
            loadedModTime = int(loadedModValue)
        except TypeError:
            loadedModTime = -1
        if modTime > loadedModTime:
            graph.remove((dataUri, LAST_MOD, loadedModValue))
            graph.remove_context(graph.context_id(dataUri))
            print "Loading: %s" % dataUri
            graph.load(fname, publicID=dataUri, **kwargs)
            graph.add((dataUri, LAST_MOD, modTime))

    return load_data

