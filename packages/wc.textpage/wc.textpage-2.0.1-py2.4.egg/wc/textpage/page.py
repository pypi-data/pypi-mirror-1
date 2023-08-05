from persistent import Persistent
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.component import adapts
from zope.size.interfaces import ISized
from zope.filerepresentation.interfaces import IReadFile, IWriteFile
from wc.textpage.interfaces import IPage
_ = MessageFactory('wc.textpage')

class Page(Persistent):
    implements(IPage)

class PageSize(object):
    """Size adapter for `Page`.

    Size for sorting:

      >>> page = Page()
      >>> page.text = u'Bla bla bla'
      >>> size = PageSize(page)
      >>> size.sizeForSorting()
      ('byte', 11)

    Size for display:

      >>> from zope.i18n import translate
      >>> translate(size.sizeForDisplay())
      u'11 characters'
    """
    implements(ISized)
    adapts(IPage)

    def __init__(self, context):
        self.context = context

    def sizeForSorting(self):
        return ('byte', len(self.context.text))

    def sizeForDisplay(self):
        unit, chars = self.sizeForSorting()
        return _('${chars} characters', mapping={'chars': chars})

class PageFile(object):
    """File representation adapter for `Page`.

    Consider a simple page with some text, possibly unicode:

      >>> page = Page()
      >>> page.text = u'Bla bla \xecf'

    The adapter will always encode to UTF-8:

      >>> file = PageFile(page)
      >>> file.read() == page.text.encode('utf-8')
      True

    Writing the stuff that was read shouldn't change the page:

      >>> text = page.text
      >>> file.write(file.read())
      >>> page.text == text
      True

    Of course, that could just be a trick that the adapter didn't do
    anything:

      >>> file.write('foobar')
      >>> page.text
      u'foobar'
    """
    implements(IReadFile, IWriteFile)
    adapts(IPage)

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.text.encode('utf-8')

    def size(self):
        return len(self.context.text.encode('utf-8'))

    def write(self, data):
        self.context.text = data.decode('utf-8')
