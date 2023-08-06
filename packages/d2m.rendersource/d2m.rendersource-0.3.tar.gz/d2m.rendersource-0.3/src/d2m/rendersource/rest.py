import os.path
import docutils.core
from zope.app.renderer.rest import HTMLTranslator, Writer, \
    ReStructuredTextSourceFactory, ReStructuredTextToHTMLRenderer
from zope.app.applicationcontrol.runtimeinfo import RuntimeInfo

import grok

def _developer_mode(context):
    return RuntimeInfo(context).getDeveloperMode()=='On'

class RSTToHTMLRenderer(ReStructuredTextToHTMLRenderer):

    def render(self, settings_overrides={}):
        # default settings for the renderer
        overrides = {
            'halt_level': 6,
            'input_encoding': 'unicode',
            'output_encoding': 'unicode',
            'initial_header_level': 3,
            }
        overrides.update(settings_overrides)
        writer = Writer()
        writer.translator_class = HTMLTranslator
        html = docutils.core.publish_string(
            self.context,
            writer=writer,
            settings_overrides=overrides,
            )
        return html

class RSTTemplateBase(grok.components.GrokTemplate):
    
    def __init__(self, string=None, filename=None, _prefix=None):
        super(RSTTemplateBase, self).__init__(string=string, filename=filename, _prefix=_prefix)
        self.string=string
        self.filename=filename
        self._prefix=_prefix
        
    def setFromString(self, string):
        self._template = ReStructuredTextSourceFactory(string)
        
    def setFromFilename(self, filename, _prefix=None):
        file = open(os.path.join(_prefix, filename))
        self._template = ReStructuredTextSourceFactory(file.read())
        
    def render(self, view):
        view.response.setHeader('Content-Type','text/html')
        settings_overrides=self.getNamespace(view).get('settings_overrides',{})
        if _developer_mode(self):
            self.setFromFilename(self.filename, self._prefix)
        return RSTToHTMLRenderer(self._template, view.request).render(settings_overrides=settings_overrides)
        
class RSTTemplateFactory(grok.GlobalUtility):

    grok.implements(grok.interfaces.ITemplateFileFactory)
    grok.name('rst')

    def __call__(self, filename, _prefix=None):
        return RSTTemplateBase(filename=filename, _prefix=_prefix)
