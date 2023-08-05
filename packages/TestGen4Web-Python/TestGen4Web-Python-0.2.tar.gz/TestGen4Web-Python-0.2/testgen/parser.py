from pdis.xpath import lexer, atoms
try:
    import cElementTree as ElementTree
except ImportError:
    from elementtree import ElementTree

legalActions = [
    'goto',
    'verify-title',
    'assert-text-exists',
    'assert-text-does-not-exist',
    'fill',
    'click',
    'check',
    'sleep',
    ]

validFormFields = [
    'input',
    'select',
    ]

def stringifyTokens(tokens):
    padded = []
    for token in tokens:
        if token in lexer.operator_names:
            token = " %s " % token
        padded.append(token)
    return ''.join([str(x) for x in padded ])

def parseXML(filename):
    """
    Parse a TestGen4Web XML file and return a list of dictionaries
    containing "actions".  User should act accordingly based on "type" 
    found.
    """
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    
    actionElems = root.findall('*/action')
    actions = []
    for elem in actionElems:
        hash = elem.attrib
        for child in elem:
            text = child.text or ''
            hash[child.tag] = text.strip()
        actions.append(hash)
    return actions

class Parser(object):
    """
    Base utility class for people who wish to parse TestGen4Web Actions and
    dispatch on those actions. Subclasses should implement the actions which 
    raise NotImplementedError.

    >>> p = Parser({})

    >>> path = '*/FORM[2]/*/INPUT[@TYPE="text" and @NAME="pager"]'
    >>> p.getFormName(path)
    >>> p.getFormID(path)
    >>> p.getFormIndex(path)
    2
    >>> p.getFormIdentity(path)
    2
    >>> p.getFormElementPath(path)
    '[@TYPE="text" and @NAME="pager"]'
    >>> p.getFormElementType(path)
    'text'
    >>> p.getFormElementName(path)
    'pager'

    >>> path = '*/FORM[2]/*/INPUT[@NAME="manage_editUserSettings:method"and @VALUE=" Save "]'
    >>> p.getFormName(path)
    >>> p.getFormID(path)
    >>> p.getFormIndex(path)
    2
    >>> p.getFormIdentity(path)
    2
    >>> p.getFormElementPath(path)
    '[@NAME="manage_editUserSettings:method" and @VALUE=" Save "]'
    >>> p.getFormElementName(path)
    'manage_editUserSettings:method'
    >>> p.getFormElementValue(path)
    ' Save '

    >>> path = '*/FORM[@NAME="loginform"]/*/INPUT[@TYPE="submit"and @VALUE="Submit"]'
    >>> p.getFormName(path)
    'loginform'
    >>> p.getFormID(path)
    >>> p.getFormIndex(path)
    >>> p.getFormIdentity(path)
    'loginform'
    >>> p.getFormElementPath(path)
    '[@TYPE="submit" and @VALUE="Submit"]'
    >>> p.getFormElementType(path)
    'submit'
    >>> p.getFormElementValue(path)
    'Submit'

    # now for some links
    >>> link = 'TD[@ID="settings"]/*/A[@CDATA="Logout"]'
    >>> p.getLinkName(link)
    'Logout'
    >>> link = 'TD[@ID="Td:3"]/TABLE[1]/TBODY[1]/TR[1]/TD[2]/TABLE[1]/TBODY[1]/TR[1]/TD[2]/TABLE[1]/TBODY[1]/TR[1]/TD[1]/A[@CDATA="Origin of Symmetry"]'
    >>> p.getLinkName(link)
    'Origin of Symmetry'
    """
    def __init__(self, actions):
        self.actions = actions

    def _getSubPath(self, xpath, names):
        s = lexer.TokenStream(xpath)
        while s.tokens:
            t = s.tokens.pop(0)
            if isinstance(t, atoms.NameTest):
                element = t.local_part
            else:
                continue
            if element.lower() in names:
                newPath = stringifyTokens(s.tokens)
                return newPath

    def _getElementAttr(self, xpath, attrName):
        element = lexer.TokenStream(xpath)
        value = None
        # iterate through the tokens comprising the path
        while element.tokens:
            attrToken = element.tokens.pop(0)
            thisAttrName = None
            # we need to say where to stop -- if we've gotten to a ']' string
            # token, then we're at the end of the attributes block
            if isinstance(attrToken, str) and attrToken == ']':
                return None
            # now do atom-type checks
            elif isinstance(attrToken, atoms.NameTest):
                thisAttrName = attrToken.local_part
            elif isinstance(attrToken, atoms.Literal):
                thisAttrName = attrToken.value
            elif isinstance(attrToken, atoms.Number) and attrName == 'index':
                return int(attrToken.value)
            # once we've got the name, get the string value for the attr
            if thisAttrName and thisAttrName.lower() == attrName.lower():
                operator = element.tokens.pop(0)
                value = element.tokens.pop(0)
            if value:
                return value.value

    def _getElementText(self, xpath):
        return self._getElementAttr(xpath, 'cdata')

    def getForm(self, xpath):
        """
        This needs to be implemented by subclasses, since every tool represents
        forms in their own unique way.
        """
        raise NotImplemented

    def getFormPath(self, xpath):
        return self._getSubPath(xpath, ['form'])

    def getFormElementPath(self, xpath):
        names = validFormFields
        return self._getSubPath(xpath, names)

    def getLinkPath(self, xpath):
        return self._getSubPath(xpath, ['a'])

    def getLinkName(self, xpath):
        path = self.getLinkPath(xpath)
        return self._getElementText(path)

    def getFormID(self, xpath):
        path = self.getFormPath(xpath)
        return self._getElementAttr(path, 'id')

    def getFormName(self, xpath):
        path = self.getFormPath(xpath)
        return self._getElementAttr(path, 'name')

    def getFormIndex(self, xpath):
        path = self.getFormPath(xpath)
        return self._getElementAttr(path, 'index')

    def getFormIdentity(self, xpath):
        ident = self.getFormID(xpath)
        if not ident:
            ident = self.getFormName(xpath)
            if not ident:
                ident = self.getFormIndex(xpath)
        return ident

    def getFormElementName(self, xpath):
        path = self.getFormElementPath(xpath)
        return self._getElementAttr(path, 'name')

    def getFormElementValue(self, xpath):
        path = self.getFormElementPath(xpath)
        return self._getElementAttr(path, 'value')

    def getFormElementType(self, xpath):
        path = self.getFormElementPath(xpath)
        return self._getElementAttr(path, 'type')

    def getFormElementID(self, xpath):
        path = self.getFormElementPath(xpath)
        return self._getElementAttr(path, 'id')

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
