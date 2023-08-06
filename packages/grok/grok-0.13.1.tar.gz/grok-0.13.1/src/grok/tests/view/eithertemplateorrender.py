"""
Only one, either a template, or render() can be specified:

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
    ...
  ConfigurationExecutionError: martian.error.GrokError: Multiple possible ways to render view
  <class 'grok.tests.view.eithertemplateorrender.CavePainting'>.
  It has both a 'render' method as well as an associated template.
  in:
"""
import grok

class Mammoth(grok.Model):
    pass

class CavePainting(grok.View):
    def render(self):
        pass

cavepainting = grok.PageTemplate("nothing")
