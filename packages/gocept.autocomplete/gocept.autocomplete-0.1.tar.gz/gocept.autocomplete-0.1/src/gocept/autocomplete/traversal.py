# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.interface
import zope.security.proxy
import zope.traversing.interfaces


class WidgetTraversable(object):
    zope.interface.implements(zope.traversing.interfaces.ITraversable)

    def __init__(self, context, request):
        # XXX security!!
        self.context = zope.security.proxy.removeSecurityProxy(context)
        self.request = request

    def traverse(self, name, remaining):
        form = self.context
        form.update()
        return form.widgets[name]

