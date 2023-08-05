import sys
import unittest
import warnings

from handler import MechanizeUnitHandler as UnitTestHandler

#warnings.filterwarnings('ignore', category=DeprecationWarning)

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
        fieldValue = action['value']
        print "Step %s: filling form '%s' with %s=%s ... " % (self.step,
            self.getFormIdentity(xpath), fieldName, fieldValue)
        try:
            self.browser[fieldName] = fieldValue
        except TypeError:
            self.browser[fieldName] = [fieldValue]

    def check(self, action):
        xpath = action['xpath']
        form = self.getForm(xpath)
        name = self.getFormElementName(xpath)
        value = self.getFormElementValue(xpath)
        print "Step %s: checking box %s=%s ..." % (self.step, name, value)
        collection = form._find_control(name, None, None, None, None, None,
            None)
        for item in collection.get_items():
            if (item.attrs.get('value') == value or 
                item.attrs.get('name') == name):
                if action['value'] == 'false':
                    item.selected = False
                elif action['value'] == 'true':
                    item.selected = True
                return

    def click(self, action):
        xpath = action['xpath']
        if xpath.startswith("*/FORM"):
            form = self.getForm(xpath)
            fieldName = self.getFormElementName(xpath)
            fieldValue = self.getFormElementValue(xpath)
            print "Step %s: clicking %s=%s on form '%s' ... " % (self.step,
                fieldName, fieldValue, self.getFormIdentity(xpath))
            if fieldName:
                clickable = form.find_control(fieldName)
                if clickable.type == 'radio':
                    for item in clickable.get_items():
                        if item.attrs.get('value') == fieldValue:
                            item.selected = True
                            return
                else:
                    request = form.click(id=clickable.id, name=clickable.name)
                    self.response = self.browser.submit(id=clickable.id,
                        name=clickable.name)
            else:
                self.response = self.browser.submit()
        elif '/A[' in xpath:
            linkName = self.getLinkName(xpath)
            print "Step %s: clicking link '%s' ... " % (self.step, linkName)
            self.response = self.browser.follow_link(text=linkName)

    def select(self, action):
        xpath = action['xpath']
        form = self.getForm(xpath)
        fieldName = self.getFormElementName(xpath)
        fieldValue = action['value']
        print "Step %s: selected %s=%s on form '%s' ... " % (self.step,
            fieldName, fieldValue, self.getFormIdentity(xpath))
        if fieldName:
            selectable = form.find_control(fieldName)
            for item in selectable.get_items():
                if item.attrs.get('value') == fieldValue:
                    item.selected = True
                    return

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
