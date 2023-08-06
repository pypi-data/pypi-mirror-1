# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import subprocess
import sys
import webbrowser
import xml.sax.saxutils
import zc.selenium.pytest


if sys.platform == 'darwin':
    # Register a Firefox browser for Mac OS X.
    class MacOSXFirefox(webbrowser.BaseBrowser):
        def open(self, url, new=0, autoraise=1):
            proc = subprocess.Popen(
                ['/usr/bin/open', '-a', 'Firefox', url])
            proc.communicate()
    webbrowser.register('Firefox', MacOSXFirefox, None, -1)


class AutocompleteTest(zc.selenium.pytest.Test):
    def test_autocomplete(self):
        s = self.selenium

        # XXX: logging in this way on /demo directly (which does not *require*
        # login) does not work
        s.open('http://mgr:mgrpw@%s/manage' % self.selenium.server)

        s.open('/demo')
        s.comment('Typing a key should cause the word to be completed')
        # XXX: this *looks* like we're entering 'rr' (when one observes the
        # browser), but it does the right thing -- and all other combination
        # of calls I tried didn't work at all. :-(
        s.type('id=form-widgets-color', 'r')
        s.typeKeys('id=form-widgets-color', 'r')
        s.waitForValue('id=form-widgets-color', 'red')
        s.verifyText('id=form-widgets-color-container', '*red*')
