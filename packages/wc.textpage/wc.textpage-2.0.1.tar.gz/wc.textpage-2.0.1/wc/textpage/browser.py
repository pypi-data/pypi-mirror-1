from zope.component import createObject, getMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile

class ViewPage(BrowserPage):

    __call__ = ViewPageTemplateFile('view.pt')

    def render(self):
        source = createObject(self.context.type, self.context.text)
        view = getMultiAdapter((source, self.request))
        return view.render()
