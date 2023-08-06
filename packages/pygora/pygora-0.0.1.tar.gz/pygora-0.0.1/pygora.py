#!/usr/bin/env python
#
# Copyright (c) 2009-2010 Alfredo Deza <alfredodeza [at] gmail [dot] com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os

class Pygora(object):
    """Discover the test files, read them line by line and then
    compare them with non-test code"""

    def __init__(self,
            path = os.getcwd()):
        self.path = path
        self.test_lines = 0
        self.source_lines = 0

    def locate_py(self):
        """Search for source and test files"""
        for root, dirs, files in os.walk(self.path):
            for item in files:
                if item.lower().endswith("py"):
                    absolute_path = os.path.join(root, item)
                    if "test" in item.lower():
                        print "Test lines:\t%s\t\t %s" % (
                                self.line_count(absolute_path), item)
                    else:
                        print "Python lines:\t%s\t\t %s" % (
                                self.line_count(absolute_path), item)

    def line_count(self, source_file):
        """Count all the code lines in a file"""
        count = 0
        open_file = open(source_file)
        for line in open_file.read().split('\n'):
            if self.skip_line(line):
                if self.recognize(source_file) == 'Test':
                    self.test_lines += 1
                else:
                    self.source_lines += 1
                count += 1
        return "%d" % count

    def skip_line(self, line):
        """Determines if this is a source line or something
        pygora should be skipping"""
        if line.startswith('#'): #no lines with comments
            return False
        elif line.startswith('"'): #no lines with docstrings
            return False
        elif not line.strip(): #do not count empty lines
            return False
        else:
            return True

    def recognize(self, file_name):
        """Return the type of the file we are dealing with:
        test or source"""
        if file_name.lower().endswith("py"):
            if 'test' in file_name.lower():
                return 'Test'
            else:
                return 'Source'

def main():
    """Parse the options"""
    run = Pygora()
    run.locate_py()
   
    print "\nTotal test lines = %s" % run.test_lines
    print "Total source lines = %s" % run.source_lines
    #lets get a nice percentage:
    if run.source_lines == 0:
        print 'Your test code is 100% of your source code\n'
    else:
        percentage = run.test_lines * 100 / run.source_lines
        print 'Your test code is %d%% of your source code\n' % percentage

if __name__ == "__main__":
    main()


