import sys
sys.path += '..'
from py2dot import *
import unittest

class ElementTest(unittest.TestCase):
    def testDottedName(self):
        code = [287, [1, 'time']]
        dn = DottedName().parse(code)
        self.assertEqual(dn.name, 'time')

    def testDottedAsName(self):
        code = [284, [287, [1, 'time']]]
        dan = DottedAsName().parse(code)
        self.assertEqual(dan.name, 'time')

    def testDottedAsNames(self):
        code = [286, [284, [287, [1, 'time']]], [12, ','], 
                     [284, [287, [1, 'clock']]]]
        dans = DottedAsNames().parse(code)
        self.assertTrue(any(d.name == 'time' for d in dans))
        self.assertTrue(any(d.name == 'clock' for d in dans))

    def testImportFrom(self):
        code = [282, [1, 'from'], [287, [1, 'socket']], 
                [1, 'import'], [285, [283, [1, 'me'], 
                    [1, 'as'], [1, 'you']]]]
        imf = ImportFrom().parse(code)
        self.assertTrue(any(i.name == 'socket' for i in imf))

    def testImportName(self):
        code = [281, [1, 'import'], 
                [286, [284, [287, [1, 'time']]], [12, ','], 
                      [284, [287, [1, 'clock']]]]]
        imn = ImportName().parse(code)
        self.assertTrue(any(i.name == 'time' for i in imn))
        self.assertTrue(any(i.name == 'clock' for i in imn))

if __name__ == '__main__':
    unittest.main()
