Autocomplete widget
===================

gocept.autocomplete provides an autocomplete widget for z3c.form based on YUI
AutoComplete.

>>> import zope.app.testing.functional
>>> root = zope.app.testing.functional.getRootFolder()
>>> import gocept.autocomplete.tests.color
>>> house = gocept.autocomplete.tests.color.House()
>>> root['house'] = house

>>> import zope.testbrowser.testing
>>> b = zope.testbrowser.testing.Browser()
>>> b.handleErrors = False

The AutocompleteWidget is an enhanced TextWidget. Thus, in display mode, it
behaves just like a TextWidget:

>>> b.open('http://localhost/house')
>>> print b.contents
<?xml...
...<span id="form-widgets-color" class="text-widget autocomplete required choice-field"></span>...

But in edit mode, it generates additional javascript code:

>>> b.addHeader('Authorization', 'Basic mgr:mgrpw')
>>> b.open('http://localhost/house')
>>> print b.contents
<?xml...
...<script src=".../autocomplete-min.js"...
...<input id="form-widgets-color"...
...<div id="form-widgets-color-container"...
...DS_XHR("http://localhost/house/@@index.html/++widget++color/@@autocomplete-search"...
...new YAHOO.widget.AutoComplete( "form-widgets-color", "form-widgets-color-container"...

The autocompletion is populated via a view registered on the widget:

>>> b.open('http://localhost/house/@@index.html/++widget++color/@@autocomplete-search')
>>> print b.contents
>>> b.open('http://localhost/house/@@index.html/++widget++color/@@autocomplete-search?q=r')
>>> print b.contents
red
ruby

But we can still enter any value we want and have it saved:

>>> b.open('http://localhost/house')
>>> b.getControl('Color').value = 'foo'
>>> b.getControl(name='form.buttons.apply').click()
>>> print b.contents
<?xml...
...foo...
