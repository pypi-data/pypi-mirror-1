
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

PloneTestCase.installProduct('ifSearchMonitor')
PloneTestCase.installProduct('TextIndexNG3')
PloneTestCase.setupPloneSite(products=('ifSearchMonitor', 'TextIndexNG3'))

class TestSuggest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.txng_convert_indexes()
        self.portal.invokeFactory(id='test1', title='test1', description='Hiv infection and other infecting diseases', type_name='Document')
        self.portal.invokeFactory(id='test2', title='test2', description='Infection, AIDS, and something else', type_name='Document')

    def testWordSuggestIndexed(self):
        sug = self.portal.ifSearchMonitor_tool.suggestWordSpelling('infecting')
        self.assert_('infecting' in sug)

    def testWordSuggestNoIndexed(self):
        sug = self.portal.ifSearchMonitor_tool.suggestWordSpelling('infectin')
        self.assert_('infectin' not in sug)
        self.assert_('infection' in sug)

    def testSpellingSuggestCaseInsensitive(self):
        sug = self.portal.ifSearchMonitor_tool.getSpellingSuggestion('Hiv Infectin')
        self.assertEqual(sug, 'hiv infection')

    def testSpellingSuggest(self):
        sug = self.portal.ifSearchMonitor_tool.getSpellingSuggestion('hiv infectin')
        self.assertEqual(sug, 'hiv infection')

    def testSpellingSuggestQuoted(self):
        sug = self.portal.ifSearchMonitor_tool.getSpellingSuggestion('"hiv infectin"')
        self.assertEqual(sug, '"hiv infection"')

    def testSpellingSuggestOneWordQuoted(self):
        sug = self.portal.ifSearchMonitor_tool.getSpellingSuggestion('"hhiv"')
        self.assertEqual(sug, '"hiv"')

    def testSpellingNotRepeatSuggest(self):
        sug = self.portal.ifSearchMonitor_tool.getSpellingSuggestion('infection or infectin')
        self.assertEqual(sug, 'infection or infecting')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSuggest))
    return suite

if __name__ == '__main__':
    framework()

