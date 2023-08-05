from zope.interface import Interface
from zope.schema import SourceText, Choice
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('wc.textpage')

class IPage(Interface):
    """A very very simple page."""

    text = SourceText(
        title=_(u"Text"),
        description=_(u"Text of the page."),
        default=u"",
        required=True
        )

    type = Choice(
        title=_(u"Text type"),
        description=_(u"Type of the text, e.g. structured text"),
        default=u"zope.source.rest",
        required = True,
        vocabulary = "SourceTypes"
        )
