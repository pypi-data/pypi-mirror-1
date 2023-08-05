"""
Using the @grok.action decorator, different actions can be defined on a
grok.EditForm. When @grok.action is used, the default behaviour (the 'Apply'
action) is not available anymore, but it can triggered manually by calling
self.applyChanges(action, data).

  >>> import grok
  >>> from grok.ftests.form.actions import Mammoth
  >>> grok.grok('grok.ftests.form.actions')
  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/manfred/@@edit")
  >>> browser.getControl(name="form.name").value = "Manfred the Mammoth"
  >>> browser.getControl(name="form.size").value = "Really big"
  >>> browser.getControl("Apply").click()
  >>> print browser.contents
  <html>...
  ...Manfred the Mammoth...
  ...Really big...
  ...

  >>> browser.open("http://localhost/manfred/@@edit")
  >>> browser.getControl(name="form.name").value = "Manfred the Second"
  >>> browser.getControl("Hairy").click()
  >>> print browser.contents
  <html>...
  ...Manfred the Second...
  ...Really big and hairy...
  ...
"""
import grok
from zope import schema

class Mammoth(grok.Model):
    class fields:
        name = schema.TextLine(title=u"Name")
        size = schema.TextLine(title=u"Size")

class Edit(grok.EditForm):
    @grok.action("Apply")
    def handle_apply(self, **data):
        self.applyChanges(**data)

    @grok.action("Hairy")
    def handle_hairy(self, **data):
        self.applyChanges(**data)
        self.context.size += " and hairy"
