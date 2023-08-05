import sys

from parser import parseXML
from handler import TestBrowserBaseCodeHandler as Handler

class TestBrowserCodeHandler(Handler):
    
    def process(self):
        self.code("from zope.testbrowser.browser import Browser")
        self.code("browser = Browser()")
        super(TestBrowserCodeHandler, self).process()

    def goto(self, action):
        self.code('browser.open("%s")' % action['value'])

    def verifyTitle(self, action):
        self.code('browser.title == "%s"' % action['value'])

    def assertTextExists(self, action):
        text = action["value"]
        self.code('"%s" in browser.contents' % text)

    def assertTextDoesNotExist(self, action):
        text = action["value"]
        self.code('"%s" not in browser.contents' % text)

    def fill(self, action):
        xpath = action['xpath']
        self.code(self.getForm(xpath))
        fieldName = self.getFormElementName(xpath)
        fieldValue = action['value']
        if fieldName:
            self.code('field = form.getControl(name="%s")' % fieldName)
            self.code('field.value = "%s"' % fieldValue)

    def check(self, action):
        xpath = action['xpath']
        self.code(self.getForm(xpath))
        form = self.getForm(xpath)
        name = self.getFormElementName(xpath)
        value = self.getFormElementValue(xpath)
        collections = form.getControl(name=name)
        box = collections.getControl(value=value)
        box.click()

    def click(self, action):
        xpath = action['xpath']
        if xpath.startswith("*/FORM"):
            self.code(self.getForm(xpath))
            fieldName = self.getFormElementName(xpath)
            fieldValue = self.getFormElementValue(xpath)
            self.code('form.submit("%s")' % fieldValue)
        elif '/A[' in xpath:
            linkName = self.getLinkName(xpath)
            self.code('link = browser.getLink("%s")' % linkName)
            self.code('link.click()')


class TestBrowserDocTestHandler(TestBrowserCodeHandler):

    def code(self, text):
        self.output += ">>> "
        super(TestBrowserDocTestHandler, self).code(text)

    def verifyTitle(self, action):
        super(TestBrowserDocTestHandler, self).verifyTitle(action)
        super(TestBrowserDocTestHandler, self).code('True')

    def assertTextExists(self, action):
        super(TestBrowserDocTestHandler, self).assertTextExists(action)
        super(TestBrowserDocTestHandler, self).code('True')

    def assertTextDoesNotExist(self, action):
        super(TestBrowserDocTestHandler, self).assertTextDoesNotExist(action)
        super(TestBrowserDocTestHandler, self).code('True')

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    if len(sys.argv) >= 3:
        outputType = sys.argv[2]
        if 'doctest' in outputType:
            handler = TestBrowserDocTestHandler
    else:
        handler = TestBrowserCodeHandler
    actions = parseXML(filename)
    t = handler(actions)
    t.process()
    print t.getResults()

