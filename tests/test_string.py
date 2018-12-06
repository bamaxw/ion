'''Testing ion.string functionalities'''
import unittest
from hypothesis import given
from hypothesis.strategies import text, lists

from ion import string

EMPTY = ''
EMPTY_LINES = '''


'''
ONE_LINE = 'dsfgdfgioj2545i43j6#12``124{}@~:@@@@>:'
NO_SPACE_LINES = '''
max
max
max
'''
SAME_INDENT = '''
    max
    max
    max
'''
DIFF_INDENT = '''
    max
        max
            max
'''

multiline_strings = lists(text()).map(lambda lines: '\n'.join(lines))

class StringTestCase(unittest.TestCase):
    '''Test case for ion.string'''
    def test_ltrim_multiline_no_kwargs(self):
        '''
        Test ltrim_multiline output with all standard strings
        No arguments attached
        '''
        self.assertEqual(
            string.ltrim_multiline(EMPTY),
            ['']
        )
        self.assertEqual(
            string.ltrim_multiline(EMPTY_LINES),
            ['' for _ in enumerate(EMPTY_LINES.split('\n'))]
        )
        self.assertEqual(
            string.ltrim_multiline(ONE_LINE),
            [ONE_LINE]
        )
        self.assertEqual(
            string.ltrim_multiline(NO_SPACE_LINES),
            NO_SPACE_LINES.split('\n')
        )
        self.assertEqual(
            string.ltrim_multiline(SAME_INDENT),
            [line.strip() for line in SAME_INDENT.split('\n')]
        )
        self.assertEqual(
            string.ltrim_multiline(DIFF_INDENT),
            [line.strip() for line in DIFF_INDENT.split('\n')]
        )

    def test_ltrim_multiline_kwargs(self):
        self.assertEqual(
            string.ltrim_multiline(EMPTY, max_no=10),
            ['']
        )
        self.assertEqual(
            string.ltrim_multiline(EMPTY_LINES, max_no=10),
            ['' for _ in enumerate(EMPTY_LINES.split('\n'))]
        )
        self.assertEqual(
            string.ltrim_multiline(ONE_LINE, max_no=10),
            [ONE_LINE]
        )
        self.assertEqual(
            string.ltrim_multiline(NO_SPACE_LINES, max_no=10),
            NO_SPACE_LINES.split('\n')
        )
        self.assertEqual(
            string.ltrim_multiline(SAME_INDENT, max_no=10),
            [line.strip() for line in SAME_INDENT.split('\n')]
        )
        self.assertEqual(
            string.ltrim_multiline(DIFF_INDENT, max_no=10),
            ['', 'max', 'max', '  max', '']
        )

    @given(multiline_strings)
    def test_ltrim_multiline_hypothesis(self, random_string):
        self.assertEqual(
            len(random_string.split('\n')),
            len(string.ltrim_multiline(random_string))
        )
        for line, trimmed in zip(random_string.split('\n'), string.ltrim_multiline(random_string)):
            self.assertLessEqual(
                trimmed.count(' '),
                line.count(' ')
            )
        for line, trimmed in zip(random_string.split('\n'), string.ltrim_multiline(random_string, max_no=2)):
            line_spaces = line.count(' ')
            trim_spaces = trimmed.count(' ')
            self.assertLessEqual(
                line_spaces - trim_spaces,
                2
            )
