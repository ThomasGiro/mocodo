#!/usr/bin/python
# encoding: utf-8

import unittest
from mocodo.attribute import *


class OuterSplitTest(unittest.TestCase):

    def test_run(self):
        self.assertEqual(
            outer_split(""),
            []
        )
        self.assertEqual(
            outer_split("aaa,bbb,ccc"),
            ["aaa", "bbb", "ccc"]
        )
        self.assertEqual(
            outer_split("aaa , bbb , ccc"),
            ["aaa", "bbb", "ccc"]
        )
        self.assertEqual(
            outer_split("aaa [ddd, eee],bbb,ccc"),
            ["aaa [ddd, eee]", "bbb", "ccc"]
        )
        self.assertEqual(
            outer_split("aaa,bbb,"),
            ["aaa", "bbb", ""]
        )
        self.assertEqual(
            outer_split("aaa [,],bbb,ccc"),
            ["aaa [,]", "bbb", "ccc"]
        )
        self.assertEqual(
            outer_split("aaa [ddd, eee] ,bbb,ccc"),
            ["aaa [ddd, eee]", "bbb", "ccc"]
        )

if __name__ == '__main__':
    unittest.main()
