"""
Forms cannot define a render method. Here we show the case where the
EditForm has an explicit template associate with it.

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
  ...
  GrokError: It is not allowed to specify a custom 'render' method for
  form <class 'grok.tests.form.norender.Edit'>. Forms either use the default
  template or a custom-supplied one.
  
"""

import grok

class Mammoth(grok.Model):
    pass

class Edit(grok.EditForm):
    # not allowed to have a render method
    def render(self):
        return "this cannot be"
    
edit = grok.PageTemplate('Foo!')
