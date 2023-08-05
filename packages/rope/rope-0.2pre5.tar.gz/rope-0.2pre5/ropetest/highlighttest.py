import unittest

from ropetest.mockeditortest import GraphicalEditorFactory, MockEditorFactory
from rope.highlight import PythonHighlighting, HighlightingStyle

class HighlightTest(unittest.TestCase):
    __factory = MockEditorFactory()
    def setUp(self):
        self.editor = self.__factory.create()
        self.highlighting = PythonHighlighting()
        unittest.TestCase.setUp(self)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def _assertOutcomesEquals(self, text, expected, not_expected=[], start=None, end=None):
        self.editor.set_text(text)
        startIndex = self.editor.get_start()
        if start is not None:
            startIndex = self.editor.get_index(start)
        endIndex = self.editor.get_end()
        if end is not None:
            endIndex = self.editor.get_index(end)
        highlights = []
        for result in self.highlighting.highlights(self.editor, startIndex, endIndex):
            highlights.append(result)
        for highlight in expected:
            current = (self.editor.get_index(highlight[0]),
                       self.editor.get_index(highlight[1]), highlight[2])
            self.assertTrue(current in highlights)
        for highlight in not_expected:
            current = (self.editor.get_index(highlight[0]),
                       self.editor.get_index(highlight[1]), highlight[2])
            self.assertTrue(current not in highlights)

    def testKeywordHighlighting(self):
        text = 'def sample_function():\n    pass\n'
        highs = [(0, 3, 'keyword'), (27, 31, 'keyword')]
        self._assertOutcomesEquals(text, highs)

    def testKeywordHighlighting2(self):
        text = 'import re\nclass Test(object):    def f(self):\npass\n'
        highs = [(0, 6, 'keyword'), (10, 15, 'keyword'),
                 (33, 36, 'keyword'), (46, 50, 'keyword')]
        self._assertOutcomesEquals(text, highs)

    def testKeywordHighlighting3(self):
        text = '   for x in range(10):'
        highs = [(3, 6, 'keyword'), (9, 11, 'keyword')]
        self._assertOutcomesEquals(text, highs)

    def test_not_highlighting_keywords_when_partof_other_words(self):
        text = 'class_'
        not_highs = [(0, 5, 'keyword')]
        self._assertOutcomesEquals(text, [], not_highs)

    def test_not_highlighting_keywords_when_partof_other_words2(self):
        text = 'in_for_class = def3 + _def + def_ + def_while'
        not_highs = [(0, 2, 'keyword'), (3, 6, 'keyword'), (7, 12, 'keyword'),
                     (0, 2, 'keyword'), (15, 18, 'keyword'), (29, 32, 'keyword'),
                     (36, 39, 'keyword'), (40, 45, 'keyword')]
        self._assertOutcomesEquals(text, [], not_highs)

    def test_no_highlighting(self):
        from rope.highlight import NoHighlighting
        noHigh = NoHighlighting()
        text = 'def sample_function():\n    pass\n'
        expected = []
        for result in noHigh.highlights(self.editor, None, None):
            self.assertEquals(expected[0], result)
            del expected[0]
        self.assertFalse(expected)

    def test_get_styles(self):
        self.assertEquals(True, self.highlighting.get_styles().has_key('keyword'))
        self.assertTrue(isinstance(self.highlighting.get_styles()['keyword'], HighlightingStyle))

    def test_following_keywords(self):
        text = 'if not'
        highs = [(0, 2, 'keyword'), (3, 6, 'keyword')]
        self._assertOutcomesEquals(text, highs)

    def test_keywords_in_strings(self):
        text = 's = " def "'
        not_highs = [(6, 9, 'keyword')]
        self._assertOutcomesEquals(text, [], not_highs)

    def test_function_definition(self):
        text = 'def func(args):'
        highs = [(0, 3, 'keyword'), (4, 8, 'definition')]
        self._assertOutcomesEquals(text, highs)
        
    def test_class_definition(self):
        self.assertTrue('definition' in self.highlighting.get_styles())
        text = 'class Sample(object):'
        highs = [(0, 5, 'keyword'), (6, 12, 'definition')]
        self._assertOutcomesEquals(text, highs)

    def test_comments(self):
        self.assertTrue('comment' in self.highlighting.get_styles())
        text = 'a = 2 # Hello world\ntest = 12'
        highs = [(6, 19, 'comment')]
        self._assertOutcomesEquals(text, highs)

    def test_long_strings(self):
        self.assertTrue('string' in self.highlighting.get_styles())
        text = "a = '''2 # multiline \n comments'''\nb = 2"
        highs = [(4, 34, 'string')]
        self._assertOutcomesEquals(text, highs)

    def test_highlighting_a_part_of_editor(self):
        text = 'print a\nprint b\nprint c'
        highs = [(8, 13, 'keyword')]
        not_highs = [(0, 5, 'keyword'), (16, 21, 'keyword')]
        self._assertOutcomesEquals(text, highs, not_highs, start=8, end=15)
        
    def test_highlighting_builtins(self):
        self.assertTrue('builtin' in self.highlighting.get_styles())
        text = 'a = None'
        highs = [(4, 8, 'builtin')]
        self._assertOutcomesEquals(text, highs)
        

if __name__ == '__main__':
    unittest.main()
