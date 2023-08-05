import sys
import unittest
import warnings

from handler import MechanizeUnitHandler as UnitTestHandler

warnings.filterwarnings('ignore', category=DeprecationWarning)

class MechanizeUnitTest(UnitTestHandler):
    """

    """
    def goto(self, action):
        url = action['value']
        print "Step %s: opening URL %s ..." % (self.step, url)
        self.browser.open(url)

    def verifyTitle(self, action):
        title = action['value']
        print "Step %s: verifying title as '%s' ..." % (self.step, title)
        self.assertEqual(title, self.browser.title())

    def assertTextExists(self, action):
        text = action["value"]
        print "Step %s: checking for text '%s' in page ..." % (self.step, text)
        self.response.seek(0)
        self.assert_(text in self.response.read())

    def assertTextDoesNotExist(self, action):
        text = action["value"]
        print "Step %s: checking that '%s' does not appear on page ..." % (
            self.step, text)
        self.response.seek(0)
        self.assert_(text not in self.response.read())

    def fill(self, action):
        xpath = action['xpath']
        form = self.getForm(xpath)
        fieldName = self.getFormElementName(xpath)
        if ':list' in fieldName:
            fieldValue = [action['value']]
        else:
            fieldValue = action['value']
        print "Step %s: filling form '%s' with %s=%s ... " % (self.step,
            self.getFormIdentity(xpath), fieldName, fieldValue)
        self.browser[fieldName] = fieldValue

    def check(self, action):
        xpath = action['xpath']
        form = self.getForm(xpath)
        name = self.getFormElementName(xpath)
        value = self.getFormElementValue(xpath)
        print "Step %s: checking box %s=%s ..." % (self.step, name, value)
        collection = form._find_control(name, None, None, None, None, None,
            None)
        box = None
        for item in collection.get_items():
            if item.attrs.get('value') == value:
                box = item
                collection.toggle(value)
                return

    def click(self, action):
        xpath = action['xpath']
        if xpath.startswith("*/FORM"):
            form = self.getForm(xpath)
            fieldName = self.getFormElementName(xpath)
            fieldValue = self.getFormElementValue(xpath)
            print "Step %s: clicking '%s' on form '%s' ... " % (self.step,
                fieldValue, self.getFormIdentity(xpath))
            if fieldName:
                submit = form.find_control(fieldName)
                request = form.click(id=submit.id, name=submit.name)
                self.response = self.browser.submit(id=submit.id,
                    name=submit.name)
            else:
                self.response = self.browser.submit()
        elif '/A[' in xpath:
            linkName = self.getLinkName(xpath)
            print "Step %s: clicking link '%s' ... " % (self.step, linkName)
            self.response = self.browser.follow_link(text=linkName)

if __name__ == "__main__":
    filename = sys.argv[1]
    # unittest does some funky stuff with argv apparently....
    sys.argv = sys.argv[:1]
    loader = unittest.TestLoader()
    test = ZopeTestBrowserUnitTest
    test.sourceFilename = filename
    suite = loader.loadTestsFromTestCase(test)
    suite = unittest.TestSuite(suite)
    unittest.TextTestRunner().run(suite)
