"""
Multiple calls of grok.require in one class are not allowed.

  >>> grok.grok(__name__)
  Traceback (most recent call last):
  GrokError: grok.require was called multiple times in <class 'grok.tests.security.multiple_require_xmlrpc.MultipleXMLRPC'>. It may only be called once on class level.

"""
import grok
import zope.interface

grok.define_permission('permission.1')
grok.define_permission('permission.2')

class MultipleXMLRPC(grok.XMLRPC):
    grok.context(zope.interface.Interface)
    grok.require('permission.1')
    grok.require('permission.2')

    def render(self):
        pass
