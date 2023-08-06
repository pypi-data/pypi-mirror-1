# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.autocomplete.interfaces
import os
import z3c.form.field
import z3c.form.form
import z3c.form.interfaces
import z3c.form.tests
import zope.app.appsetup.bootstrap
import zope.component
import zope.interface
import zope.publisher.interfaces.browser
import zope.schema
import transaction


class ColorSource(object):
    zope.interface.implements(gocept.autocomplete.interfaces.ISearchableSource)

    _data = [u"red", u"blue", u"ruby"]

    def __iter__(self):
        for item in self._data:
            yield item

    def __contains__(self, value):
        return True

    def search(self, prefix):
        return [item for item in self if item.lower().find(prefix.lower()) == 0]


class IHouse(zope.interface.Interface):
    color = zope.schema.Choice(title=u"Color", source=ColorSource())


class House(object):
    zope.interface.implements(IHouse)

    color = None


class HouseForm(z3c.form.form.EditForm):
    fields = z3c.form.field.Fields(IHouse)

    def __call__(self, *args, **kw):
        return super(HouseForm, self).__call__(*args, **kw)


class IColorSkin(z3c.form.interfaces.IFormLayer,
                 zope.publisher.interfaces.browser.IDefaultBrowserLayer,
                 zope.publisher.interfaces.browser.IBrowserSkinType):
    pass


def init_demo(event):
    db, connection, root, root_folder = zope.app.appsetup.bootstrap.getInformationFromEvent(event)

    zope.component.provideAdapter(z3c.form.form.FormTemplateFactory(
        os.path.join(os.path.dirname(gocept.autocomplete.tests.__file__),
                     'layout.pt')))


    root_folder['demo'] = House()
    transaction.commit()
    connection.close()

