import sys
import unittest

from handler import TestBrowserUnitHandler as UnitTestHandler

class TestBrowserUnitTest(UnitTestHandler):
    """

    """
    def goto(self, action):
        url = action['value']
        print "Step %s: opening URL %s ..." % (self.step, url)
        self.browser.open(url)

    def verifyTitle(self, action):
        title = action['value']
        print "Step %s: verifying title as '%s' ..." % (self.step, title)
        self.assertEqual(title, self.browser.title)

    def assertTextExists(self, action):
        text = action["value"]
        print "Step %s: checking for text '%s' in page ..." % (self.step, text)
        self.assert_(text in self.browser.contents)

    def assertTextDoesNotExist(self, action):
        text = action["value"]
        print "Step %s: checking that '%s' does not appear on page ..." % (
            self.step, text)
        self.assert_(text not in self.browser.contents)

    def fill(self, action):
        xpath = action['xpath']
        form = self.getForm(xpath)
        fieldName = self.getFormElementName(xpath)
        fieldValue = action['value']
        print "Step %s: filling form '%s' with %s=%s ... " % (self.step,
            self.getFormIdentity(xpath), fieldName, fieldValue)
        if fieldName:
            field = form.getControl(name=fieldName)
            field.value = fieldValue

    def check(self, action):
        xpath = action['xpath']
        form = self.getForm(xpath)
        name = self.getFormElementName(xpath)
        value = self.getFormElementValue(xpath)
        print "Step %s: checking %s=%s ..." % (self.step, name, value)
        collection = form.getControl(name=name)
        box = collection.getControl(value=value)
        box.click()

    def click(self, action):
        xpath = action['xpath']
        if xpath.startswith("*/FORM"):
            form = self.getForm(xpath)
            fieldName = self.getFormElementName(xpath)
            fieldValue = self.getFormElementValue(xpath)
            print "Step %s: clicking '%s' on form '%s' ... " % (self.step,
                fieldValue, self.getFormIdentity(xpath))
            form.submit(fieldValue)
        elif '/A[' in xpath:
            linkName = self.getLinkName(xpath)
            print "Step %s: clicking link '%s' ... " % (self.step, linkName)
            link = self.browser.getLink(linkName)
            link.click()

    def select(self, action):
        self.click(action)

if __name__ == "__main__":
    filename = sys.argv[1]
    # unittest does some funky stuff with argv apparently....
    sys.argv = sys.argv[:1]
    loader = unittest.TestLoader()
    test = TestBrowserUnitTest
    test.sourceFilename = filename
    suite = loader.loadTestsFromTestCase(test)
    suite = unittest.TestSuite(suite)
    unittest.TextTestRunner().run(suite)
