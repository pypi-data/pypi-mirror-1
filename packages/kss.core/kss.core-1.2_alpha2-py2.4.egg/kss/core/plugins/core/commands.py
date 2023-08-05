from interfaces import IKSSCoreCommands
from kss.core.selectors import Selector, CssSelector, HtmlIdSelector
from kss.core.azaxview import CommandSet
from kss.core.deprecated import deprecated
from kss.core.parsers import XmlParser, HtmlParser
from kss.core.plugins.core.interfaces import IKSSCoreCommands
from zope.interface import implements

class KSSCoreCommands(CommandSet):
    implements(IKSSCoreCommands)

    def getSelector(self, type, selector):
        'Get a selector of a given type'
        return Selector(type, selector)

    def getCssSelector(self, selector):
        return CssSelector(selector)
            
    def getHtmlIdSelector(self, selector):
        return HtmlIdSelector(selector)


    # XXX the list is not full: maybe complete them?
    
    def replaceInnerHTML(self, selector, new_value):
        """ see interfaces.py """
        new_value = HtmlParser(new_value)().encode('ascii', 'xmlcharrefreplace')
        command = self.commands.addCommand('replaceInnerHTML', selector)
        data = command.addParam('html', new_value)

    def replaceHTML(self, selector, new_value):
        """ see interfaces.py """
        new_value = HtmlParser(new_value)().encode('ascii', 'xmlcharrefreplace')
        command = self.commands.addCommand('replaceHTML', selector)
        data = command.addParam('html', new_value)
    
    def setAttribute(self, selector, name, value):
        """ see interfaces.py """
        command = self.commands.addCommand('setAttribute', selector)
        data = command.addParam('name', name)
        data = command.addParam('value', value)

    def setStyle(self, selector, name, value):
        """ see interfaces.py """
        command = self.commands.addCommand('setStyle', selector)
        data = command.addParam('name', name)
        data = command.addParam('value', value)
    
    def insertHTMLAfter(self, selector, new_value):
        """ see interfaces.py """
        new_value = HtmlParser(new_value)().encode('ascii', 'xmlcharrefreplace')
        command = self.commands.addCommand('insertHTMLAfter', selector)
        data = command.addParam('html', new_value)

    def insertHTMLAsFirstChild(self, selector, new_value):
        """ see interfaces.py """
        new_value = HtmlParser(new_value)().encode('ascii', 'xmlcharrefreplace')
        command = self.commands.addCommand('insertHTMLAsFirstChild', selector)
        data = command.addParam('html', new_value)

    def insertHTMLAsLastChild(self, selector, new_value):
        """ see interfaces.py """
        new_value = HtmlParser(new_value)().encode('ascii', 'xmlcharrefreplace')
        command = self.commands.addCommand('insertHTMLAsLastChild', selector)
        data = command.addParam('html', new_value)

    def insertHTMLBefore(self, selector, new_value):
        """ see interfaces.py """
        new_value = HtmlParser(new_value)().encode('ascii', 'xmlcharrefreplace')
        command = self.commands.addCommand('insertHTMLBefore', selector)
        data = command.addParam('html', new_value)

    def clearChildNodes(self, selector):
        """ see interfaces.py """
        command = self.commands.addCommand('clearChildNodes', selector)
    
    def deleteNode(self, selector):
        """ see interfaces.py """
        command = self.commands.addCommand('deleteNode', selector)

    def deleteNodeAfter(self, selector):
        """ see interfaces.py """
        command = self.commands.addCommand('deleteNodeAfter', selector)

    def deleteNodeBefore(self, selector):
        """ see interfaces.py """
        command = self.commands.addCommand('deleteNodeBefore', selector)

    def copyChildNodesFrom(self, selector, id):
        """ see interfaces.py """
        command = self.commands.addCommand('copyChildNodesFrom', selector)
        data = command.addParam('html_id', id)

    def moveNodeAfter(self, selector, id):
        """ see interfaces.py """
        command = self.commands.addCommand('moveNodeAfter', selector)
        data = command.addParam('html_id', id)

    def copyChildNodesTo(self, selector, id):
        """ see interfaces.py """
        command = self.commands.addCommand('copyChildNodesTo', selector)
        data = command.addParam('html_id', id)

    def setStateVar(self, varname, value):
        """ see interfaces.py """
        command = self.commands.addCommand('setStateVar')
        command.addParam('varname', varname)
        command.addParam('value', value)

    def triggerEvent(self, name, **kw):
        """ see interfaces.py """
        command = self.commands.addCommand('triggerEvent')
        command.addParam('name', name)
        for key, value in kw.iteritems():
            command.addParam(key, value)

    # XXX Deprecated ones

    def moveChildrenTo(self, selector, id):
        """ see interfaces.py """
        self.copyChildrenTo(selector, id)
        self.clearChildren(selector)
    moveChildrenTo = deprecated(moveChildrenTo, 'No more supported, use a sequence of copyChildrenTo and clearChildren')

    setHtmlAsChild = deprecated(replaceInnerHTML, 'use replaceInnerHTML instead')
    addAfter = deprecated(insertHTMLAfter, 'use insertHTMLAfter instead')
    clearChildren = deprecated(clearChildNodes, 'use clearChildNodes instead')
    removeNode = deprecated(deleteNode, 'use deleteNode instead')
    removeNextSibling = deprecated(deleteNodeAfter, 'use deleteNodeAfter instead')
    removePreviousSibling = deprecated(deleteNodeBefore, 'use deleteNodeBefore instead')
    copyChildrenFrom = deprecated(copyChildNodesFrom, 'use copyChildNodesFrom instead')
    copyChildrenTo = deprecated(copyChildNodesTo, 'use copyChildNodesTo instead')
    setStatevar = deprecated(setStateVar, 'use setStateVar (capital V) instead')

    # end deprecated
