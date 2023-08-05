import unittest
import textwrap
from kss.core import AzaxUnicodeError
from kss.core.tests.base import KssViewTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite

class TestKSSViewCoreCommandSet(KssViewTestCase):
    
    def test_empty(self):
        view = self.createView()
        commands = view.getCommands()
        self.assertEqual(len(commands), 0)

    def test_addCommand(self):
        view = self.createView()
        commands = view.getCommands()
        command = commands.addCommand('replaceInnerHTML', 'selector')
        self.assertEqual(len(commands), 1)
        self.assertEqual(command.getName(), 'replaceInnerHTML')
        self.assertEqual(command.getSelector(), 'selector')
        params = command.getParams()
        self.assertEqual(len(params), 0)
        
    # XXX since lxml is gone, the next cases are no problem anymore
    # Nevertheless, we test all these cases
    
    def _checkSetHtmlResult(self, content, content2=None):
        view = self.createView()
        view.getCommandSet('core').replaceInnerHTML('div.class', content)
        commands = view.getCommands()
        self.assertEqual(len(commands), 1)
        command = commands[0]
        self.assertEqual(command.getName(), 'replaceInnerHTML')
        self.assertEqual(command.getSelector(), 'div.class')
        params = command.getParams()
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].getName(), 'html')
        if content2 == None:
            content2 = content
        self.assertEqual(params[0].getContent().encode('ascii', 'xmlcharrefreplace'), content2.encode('ascii', 'xmlcharrefreplace'))

    def test_replaceInnerHTMLTextPlusEntity(self):
        'See if non breaking space entity works'
        ##self._checkSetHtmlResult('&nbsp;')
        # XXX we remove html named entities now
        self._checkSetHtmlResult('&nbsp;', '&#160;')
        
    def test_replaceInnerHTMLTextPlusEntityOthers(self):
        'See if the other HTML entities work as well'
        # XXX we remove html named entities now
        self._checkSetHtmlResult('<p xmlns="http://www.w3.org/1999/xhtml">&raquo;Hello world!&laquo;</p>',
                   '<p xmlns="http://www.w3.org/1999/xhtml">&#187;Hello world!&#171;</p>')

    def test_replaceInnerHTMLTextOnly(self):
        self._checkSetHtmlResult('new content')

    def test_replaceInnerHTMLTagOnly(self):
        self._checkSetHtmlResult('<p xmlns="http://www.w3.org/1999/xhtml">new_content</p>')
        
    def test_replaceInnerHTMLTagPlusText(self):
        self._checkSetHtmlResult('<p xmlns="http://www.w3.org/1999/xhtml">new_content</p>after')
        
    def test_replaceInnerHTMLTextTagPlusText(self):
        self._checkSetHtmlResult('before<p xmlns="http://www.w3.org/1999/xhtml">new_content</p>after')
        
    def test_setHtmlAcceptsUnicode(self):
        'Test that it accepts unicode'
        self._checkSetHtmlResult(u'abcá')
        
    def test_setHtmlChecksForNonUnicode(self):
        'Test that it does not accept non unicode (unless pure ascii)'
        self.assertRaises(AzaxUnicodeError, self._checkSetHtmlResult, 'abcá')

class FTestKSSViewCoreCommandSet(KssViewTestCase):
    'Functional tests'

    def _wrapped_commands(self, inline):
        header = textwrap.dedent(u'''\
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml"
                      xmlns:kukit="http://www.kukit.org/commands/1.0"><body>
                <kukit:commands>
                ''')
        footer = textwrap.dedent('''\
                </kukit:commands>
                </body></html>
                ''')
        return header + inline + footer

    def assertXMLEquals(self, a, b):
        self.assertEqual(a, b)

    def assertCommandsEqual(self, a, b):
        self.assertXMLEquals(a, self._wrapped_commands(b))

    def test_empty(self):
        view = self.createView()
        result = view.render()
        self.assertEquals(view.request.response.getHeader('content-type'), 'text/xml;charset=utf-8')
        self.assertCommandsEqual(result, '')
    
    def test_replaceInnerHTML(self):
        view = self.createView()
        view.getCommandSet('core').replaceInnerHTML('div.class', 'new content')
        result = view.render()
        awaited = u'''\
<kukit:command selector="div.class" name="replaceInnerHTML"
               selectorType="">
    <kukit:param name="html">new content</kukit:param>
</kukit:command>
'''
        self.assertCommandsEqual(result, awaited)
        
    def test_setCommandSet(self):
        view = self.createView()
        cs = view.getCommandSet('core')
        cs.replaceInnerHTML('div.class', 'new content')
        result = view.render()
        awaited = u'''\
<kukit:command selector="div.class" name="replaceInnerHTML"
               selectorType="">
    <kukit:param name="html">new content</kukit:param>
</kukit:command>
'''
        self.assertCommandsEqual(result, awaited)

def afterSetUp(self):
    KssViewTestCase.afterSetUp(self)
    self.setDebugRequest()


def test_suite():
    suites = []
    suites.append(unittest.makeSuite(TestKSSViewCoreCommandSet))
    suites.append(unittest.makeSuite(FTestKSSViewCoreCommandSet))
    suites.append(FunctionalDocFileSuite('../actionwrapper.py',
                                         test_class=KssViewTestCase,
                                         setUp=afterSetUp,
                                         tearDown=KssViewTestCase.beforeTearDown.im_func))
    return unittest.TestSuite(suites)
