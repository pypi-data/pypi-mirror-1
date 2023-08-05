import sys
import unittest

from parser import Parser, parseXML

class Handler(Parser):

    actions = []
    step = 1

    def setFilename(self, filename):
        self.filename = filename

    setFilename = classmethod(setFilename)

    def process(self):
        """call this method to dispatch on the actions"""
        for a in self.actions:
            atype = a['type']
            if atype=="goto":
                self.goto(a)
            elif atype=="verify-title":
                self.verifyTitle(a)
            elif atype=="fill" or atype=="select":
                self.fill(a)
            elif atype=="click":
                self.click(a)
            elif atype=="check":
                self.check(a)
            elif atype=="assert-text-exists":
                self.assertTextExists(a)
            elif atype=="assert-text-does-not-exist":
                self.assertTextDoesNotExist(a)
            else:
                print "WARNING: Unhandled action!"
                continue
            self.step += 1

    def goto(self, action):
        raise NotImplementedError

    def verifyTitle(self, action):
        raise NotImplementedError

    def assertTextExists(self, action):
        raise NotImplementedError

    def assertTextDoesNotExist(self, action):
        raise NotImplementedError
    
    def fill(self, action):
        raise NotImplementedError 

    def click(self, action):
        raise NotImplementedError

    def check(self, action):
        raise NotImplementedError

class CodeHandler(Handler):

    def __init__(self, *args, **kwds):
        super(CodeHandler, self).__init__(*args, **kwds)
        self.output = ''

    def code(self, text):
        self.output += "%s\n" % text

    def getResults(self):
        return self.output

class TestBrowserBaseCodeHandler(CodeHandler):

    def getForm(self, xpath):
        formIdent = self.getFormName(xpath)
        if formIdent:
            form = 'form = browser.getForm(name="%s")' % formIdent
        else:
            formIdent = self.getFormID(xpath)
            if formIdent:
                form = 'form = browser.getForm(id="%s")' % formIdent
            else:
                formIdent = self.getFormIndex(xpath)
                form = 'form = browser.getForm(index="%s")' % formIdent
        return form

class UnitTestHandler(Handler, unittest.TestCase):

    sourceFilename = ''
    headers = [
            ("User-Agent", "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.10) Gecko/20050915 Firefox/1.0.6"),
            ("Accept", "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"),
            ("Accept-Language", "en-us,en;q=0.5"),
            ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7"),
            ("Keep-Alive", "300"),
            ("Connection", "keep-alive")]
    actions = []

    def __init__(self, *args, **kwds):
        unittest.TestCase.__init__(self, *args, **kwds)

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.actions = parseXML(self.sourceFilename)

    def testScript(self):
        self.process()

class MechanizeUnitHandler(UnitTestHandler):

    def setUp(self):
        from mechanize import Browser
        super(MechanizeUnitHandler, self).setUp()
        self.browser = Browser()
        # tell them we are moz...
        self.browser.addheaders = self.headers
        self.browser.set_handle_robots(0)

    def getForm(self, xpath):
        formIdent = self.getFormName(xpath)
        if formIdent:
            self.browser.select_form(name=formIdent)
        else:
            formIdent = self.getFormID(xpath)
            if formIdent:
                self.browser.select_form(id=formIdent)
            else:
                formIdent = int(self.getFormIndex(xpath)) - 1
                self.browser.select_form(nr=formIdent)
        return self.browser.form

class TestBrowserUnitHandler(UnitTestHandler):

    def setUp(self):
        from zope.testbrowser.browser import Browser
        super(TestBrowserUnitHandler, self).setUp()
        self.browser = Browser()
        # tell them we are moz...
        self.browser.mech_browser.addheaders = self.headers
        self.browser.mech_browser.set_handle_robots(0)

    def getForm(self, xpath):
        formIdent = self.getFormName(xpath)
        if formIdent:
            form = self.browser.getForm(name=formIdent)
        else:
            formIdent = self.getFormID(xpath)
            if formIdent:
                form = self.browser.getForm(id=formIdent)
            else:
                formIdent = int(self.getFormIndex(xpath)) - 1
                form = self.browser.getForm(index=formIdent)
        return form

