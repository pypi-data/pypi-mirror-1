import os.path
import docutils.core
from zope.app.renderer.rest import HTMLTranslator, Writer, \
    ReStructuredTextSourceFactory, ReStructuredTextToHTMLRenderer
from zope.app.appsetup.appsetup import getConfigContext

import codecs
import locale
import grok

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
        html = docutils.core.publish_file(
            source_path=self.context,
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
        self._cooked=False
                
    def setFromFilename(self, filename, _prefix=None):
        filename = os.path.join(_prefix, filename)
        self._template = ReStructuredTextSourceFactory(filename)
        
    def render(self, view):
        view.response.setHeader('Content-Type','text/html')
        settings_overrides=self.getNamespace(view).get('settings_overrides',{})
        if not(self._cooked) or getConfigContext().hasFeature('devmode'):
            self.setFromFilename(self.filename, self._prefix)
            self._cooked=RSTToHTMLRenderer(self._template, view.request).render(settings_overrides=settings_overrides)
        return self._cooked
    
class RSTTemplateFactory(grok.GlobalUtility):

    grok.implements(grok.interfaces.ITemplateFileFactory)
    grok.name('rst')

    def __call__(self, filename, _prefix=None):
        return RSTTemplateBase(filename=filename, _prefix=_prefix)
