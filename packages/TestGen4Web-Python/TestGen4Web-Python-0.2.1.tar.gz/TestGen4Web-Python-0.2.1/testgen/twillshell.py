from parser import parseXML
from handler import CodeHandler

class TwillShellHandler(CodeHandler):
    
    def process(self):
        self.code("debug commands 1")
        super(TwillShellHandler, self).process()

    def assertTextExists(self, action):
        regex = action["value"]
        self.code('find "%s"' % regex)

    def assertTextDoesNotExist(self, action):
        raise NotImplementedError

    def fill(self, action):
        xpath = action['xpath']
        formName = self.getFormName(xpath)
        fieldName = self.getFormElementName(xpath)
        fieldValue = action['value']
        self.code('formvalue %s %s "%s"' % (formName, fieldName, fieldValue))

    def click(self, action):
        xpath = action['xpath']
        if xpath.startswith("*/FORM"):
            # first "click" button
            formName = self.getFormName(xpath)
            fieldName = self.getFormElementName(xpath)
            fieldValue = self.getFormElementValue(xpath)
            self.code('formvalue %s %s "%s"' % (formName, fieldName, fieldValue))
            # then submit
            self.code("submit")
        elif '/A[' in xpath:
            linkName = self.getLinkName(xpath)
            self.code('follow "%s"' % linkName)
        
    def verifyTitle(self, action):
        self.code('title "%s"' % action['value'])

    def goto(self, action):
        self.code("go %s" % action['value'])

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    actions = parseXML(filename)
    t = TwillShellHandler(actions)
    t.process()
    print t.getResults()
