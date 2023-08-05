
# TODO: rewrite using only elementtree..(?)
# TODO: cannot handle ordered fallbacks (will filter all others or none)
#        - solutions may have to expand all literals, store their language and
#          fallback accordingly, or use a rather complex simultaneous iteraror
#          loop on all values.

from kid.pull import Parser, ElementStream, START, END, QuickTextReader, _coalesce
xmlLang = u'{http://www.w3.org/XML/1998/namespace}lang'

def language_filtered_xml(valueOrList, lang, fragment=1, encoding=None):
    if isinstance(valueOrList, unicode):
        values = (valueOrList,)
    else:
        values = valueOrList
    return [langXML(value, lang, fragment, encoding) for value in values if value]

def langXML(text, lang, fragment=True, encoding=None):
    """Modified version of kid.pull.XML"""
    if text.startswith('<?xml ') or text.startswith('<!DOCTYPE '):
        fragment = False
    if fragment:
        text = '<xml>%s</xml>' % text
    if isinstance(text, unicode):
        encoding = 'utf-16'
        text = text.encode(encoding)
    p = Parser(QuickTextReader(text), encoding)
    eStream = LangFilteredElementStream(lang, _coalesce(p, encoding))
    if fragment:
        return eStream.strip()
    else:
        return eStream

class LangFilteredElementStream(ElementStream):
    def __init__(self, lang, stream, current=None):
        self._langToUse = lang
        ElementStream.__init__(self, stream, current)
    def _track(self, stream, current=None):
        depth = self.current is not None and 1 or 0
        eating = False
        for ev, item in ElementStream._track(self, stream, current):
            if ev == START and self._langToUse:
                elemLang = item.get(xmlLang)
                langKey = xmlLang
                if not elemLang:
                    # FIXME: Remove this 'if'; it's a temporary solution, due
                    # to rdflib xml/rdf XMLLiteral with embedded xml:lang
                    # parsing problems..
                    langKey = "lang"
                    elemLang = item.get(langKey)
                if elemLang:
                    del item.attrib[langKey]
                    if elemLang != self._langToUse:
                        eating = True
                    elif item.tag == u'rdf-wrapper':
                        continue
            if eating == True:
                if ev == START: depth += 1
                elif ev == END:
                    depth -= 1
                    if depth == 0: eating = False
                continue
            yield ev, item

