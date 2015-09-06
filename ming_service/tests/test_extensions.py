# coding:utf-8

#import os, sys
#parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
#sys.path.append(parent_dir)

import unittest
import re

from ming.ming import HANDLERS
from settings import EXTENSIONS



class TestExtensions(unittest.TestCase):

    def test_correct_extensions(self):
        print '\n test that each settings.EXTENSIONS is correct'
        pattern = re.compile(r'^[.]{1}\w{2,4}$')
        for ext in EXTENSIONS:
            self.assertTrue(pattern.match(ext))


    def test_handlers(self):
        print '\n test that for each settings.EXTENSIONS exists handler in ming.ming.HANDLERS dict'
        set_extensions = set(EXTENSIONS)
        set_handlers = set(HANDLERS.keys())
        self.assertEqual(set_extensions, set_handlers)


if __name__ == '__main__':
    unittest.main()