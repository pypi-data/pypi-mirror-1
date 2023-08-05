"""
A permission has to be defined first (using grok.define_permission for
example) before it can be used in grok.require().

  >>> grok.grok(__name__)
  Traceback (most recent call last):
  GrokError: Undefined permission 'doesnt.exist' in <class 'grok.tests.security.missing_permission.MissingPermission'>. Use grok.define_permission first.

"""

import grok
import zope.interface

class MissingPermission(grok.View):
    grok.context(zope.interface.Interface)
    grok.require('doesnt.exist')

    def render(self):
        pass

