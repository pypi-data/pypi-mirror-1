from zope.interface import Interface, implements
from zope.schema import TextLine
from zope.component import adapts, adapter, createObject
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.renderer.rest import IReStructuredTextSource
from zope.app.renderer.stx import IStructuredTextSource
from zope.app.renderer.plaintext import IPlainTextSource
from wc.textpage.interfaces import IPage

class ITextMetadata(Interface):
    """Metadata of a text, usually sniffed with some crazy method.
    """

    title = TextLine(
        title=u"Title",
        description=u"Title of the text document."
        )

    description = TextLine(
        title=u"Description",
        description=u"Abstract or description of the text, usually the " \
        "first paragraph."
        )

class ReSTMetadata(object):
    """Extract title from ReST source.

    Consider a simple ReST document:

      >>> rest = '''\\
      ... The title
      ... =========
      ... 
      ... Some text
      ...
      ... New paragraph.
      ... 
      ... New section
      ... -----------
      ...
      ... some more text.'''
      >>> data = ReSTMetadata(rest)
      >>> data.title
      u'The title'
      >>> data.description
      u'Some text'

    The adapter also works for empty documents:

      >>> metadata = ReSTMetadata('')
      >>> metadata.title, metadata.description
      (u'', u'')

    or even invalid ones:

      >>> metadata = ReSTMetadata('foobar')
      >>> metadata.title, metadata.description
      (u'', u'foobar')

      >>> metata = ReSTMetadata('foobar\\n\\nbarfoo\\nbazbaz')
      >>> metadata.title, metadata.description
      (u'', u'foobar')
    """
    implements(ITextMetadata)
    adapts(IReStructuredTextSource)

    title = description = u''

    def __init__(self, text):
        if not text:
            return

        import docutils.parsers.rst
        parser = docutils.parsers.rst.Parser()
        doc = docutils.utils.new_document('doc')
        doc.settings.tab_width = 4
        doc.settings.pep_references = 1
        doc.settings.rfc_references = 1
        parser.parse(text, doc)
        dom = doc.asdom()

        # title
        titles = dom.getElementsByTagName('title')
        if titles:
            title = ' '.join([node.nodeValue for node in
                              titles[0].childNodes
                              if node.nodeValue])
            self.title = unicode(title)

        # description
        paras = dom.getElementsByTagName('paragraph')
        if paras:
            description = ' '.join([node.nodeValue for node in
                                    paras[0].childNodes
                                    if node.nodeValue])
            self.description = unicode(description)

class PlainTextMetadata(object):
    """Extract title from a plain text source.

      >>> text = '''\\
      ... Hello there
      ... 
      ... It's me, remember me?
      ...
      ... Oh, too bad.'''
      >>> metadata = PlainTextMetadata(text)
      >>> metadata.title
      u'Hello there'
      >>> metadata.description
      u"It's me, remember me?"

      >>> metadata = PlainTextMetadata('')
      >>> metadata.title, metadata.description
      (u'', u'')
    """
    implements(ITextMetadata)
    adapts(IPlainTextSource)

    title = description = u''

    def __init__(self, text):
        text = text.lstrip()
        if not text:
            return

        text = text.replace('\r', '')
        paras = [para for para in text.split('\n\n') if para]
        if paras:
            self.title = unicode(paras[0].strip())
        if len(paras) > 1:
            self.description = unicode(paras[1].strip())

class STXMetadata(object):
    """Extract title from a StructuredText source.

    >>> text = '''\\
    ... Hello there
    ... 
    ...   It's me, remember me?
    ...
    ...   Oh, too bad.'''
    >>> metadata = STXMetadata(text)
    >>> metadata.title
    u'Hello there'
    >>> metadata.description
    u"It's me, remember me?"

    >>> metadata = STXMetadata('')
    >>> metadata.title, metadata.description
    (u'', u'')

    >>> metata = STXMetadata('Foobar\\n\\nBarfoo')
    >>> metadata.title, metadata.description
    (u'', u'')
    """
    implements(ITextMetadata)
    adapts(IStructuredTextSource)

    title = description = u''

    def __init__(self, text):
        if not text:
            return

        import zope.structuredtext.stng
        st = zope.structuredtext.stng.structurize(text)

        paras = st.getElementsByTagName('StructuredTextParagraph')
        if paras:
            title = paras[0].getFirstChild().getNodeValue()
            self.title = unicode(title.strip())
        if len(paras) > 1:
            description = paras[1].getFirstChild().getNodeValue()
            self.description = unicode(description.strip())

@adapter(IPage, IObjectModifiedEvent)
def updateDCMetadata(page, event):
    """Update a page's DublinCore metadata according to what we sniff
    from the source text"""
    dc = IWriteZopeDublinCore(page)
    source = createObject(page.type, page.text)
    metadata = ITextMetadata(source)
    dc.title = metadata.title
    dc.description = metadata.description
