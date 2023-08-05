"""
Using the @grok.action decorator, different actions can be defined on
a grok.Form. When @grok.action is used, the default behaviour (the
'Apply' action) is not available anymore, but it can triggered
manually by calling self.apply_changes(object, data).

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
  ...Modified!...
  ...Manfred the Mammoth...
  ...Really big...
  ...

Save again without any changes:

  >>> browser.getControl("Apply").click()
  >>> print browser.contents
  <html>...
  ...No changes!...
  ...

  >>> browser.open("http://localhost/manfred/@@edit")
  >>> browser.getControl(name="form.name").value = "Manfred the Second"
  >>> browser.getControl("Hairy").click()
  >>> print browser.contents
  <html>...
  ...Manfred the Second...
  ...Really big and hairy...
  ...

  >>> browser.open("http://localhost/manfred/meet")
  >>> browser.getControl(name="form.other").value = "Ellie"
  >>> browser.getControl("Meet").click()
  >>> print browser.contents
  Manfred the Second meets Ellie
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
        if self.apply_changes(self.context, **data):
            self.status = 'Modified!'
        else:
            self.status = 'No changes!'

    @grok.action("Hairy")
    def handle_hairy(self, **data):
        self.apply_changes(self.context, **data)
        self.context.size += " and hairy"

class Meet(grok.Form):
    form_fields = grok.Fields(
        other = schema.TextLine(title=u'Mammoth to meet with')
        )

    @grok.action('Meet')
    def meet(self, other):
        return self.context.name + ' meets ' + other
