import sys
if '../' not in sys.path:
    sys.path.append('../')
import unittest
import os
from pygora import Pygora

class TestPygora(unittest.TestCase):
   
    def setUp(self):
        source_file = open('/tmp/source.py', 'w')
        test_file = open('/tmp/test_source.py', 'w')
        source_file.write("""# comment line
        def a_func():
        "docstring"
        pass
        """)
        source_file.close()
        test_file.write("""def test_source():
        pass""")
        test_file.close() 

    def tearDown(self):
        os.remove('/tmp/source.py')
        os.remove('/tmp/test_source.py')

    def test_test_lines(self):
        """Test lines should always be cero"""
        goat = Pygora(path = '.')
        expected = 0
        actual = goat.test_lines
        self.assertEqual(actual, expected)

    def test_source_lines(self):
        """Source lines should always be cero"""
        goat = Pygora(path = '.')
        expected = 0
        actual = goat.source_lines
        self.assertEqual(actual, expected)

    def test_path(self):
        """Path should always be the cwd"""
        expected = os.getcwd()
        goat = Pygora()
        actual = goat.path
        self.assertEqual(actual, expected)

    def test_skip_line_comment(self):
        """Return False if line starts with #"""
        goat = Pygora()
        line = "# a commented out line"
        actual = goat.skip_line(line)
        self.assertFalse(actual)

    def test_skip_line_docstring(self):
        """Return False if line starts with quote"""
        goat = Pygora()
        line = """"a docstring" """
        actual = goat.skip_line(line)
        self.assertFalse(actual)

    def test_skip_line_empty(self):
        """Return False if line is empty"""
        goat = Pygora()
        line = " "
        actual = goat.skip_line(line)
        self.assertFalse(actual)

    def test_recognize_Test(self):
        """Return Test if the file is a test file"""
        goat = Pygora()
        file_name = 'Test_the_goat.py'
        expected = 'Test'
        actual = goat.recognize(file_name)
        self.assertEqual(actual, expected)

    def test_recognize_Source(self):
        """Return Source if the file is a source file"""
        goat = Pygora()
        file_name = 'the_goat.py'
        expected = 'Source'
        actual = goat.recognize(file_name)
        self.assertEqual(actual, expected)

    def test_line_count(self):
        """Return the total number of lines for a file"""
        goat = Pygora()
        expected = '3'
        actual = goat.line_count('/tmp/source.py')
        self.assertEqual(actual, expected)

    def test_line_count_test(self):
        """Return the total number of lines for a test files"""
        goat = Pygora()
        expected = '2'
        actual = goat.line_count('/tmp/test_source.py')
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
