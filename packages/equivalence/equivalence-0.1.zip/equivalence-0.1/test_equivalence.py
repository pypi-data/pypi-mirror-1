#!/usr/bin/env python

import re
import unittest
from equivalence import *

urls = [
    'http://python.org/',           #0
    'http://www.python.org/',       #1
    'www.python.org/index.html',    #2

    'http://www.foobar.com/docs/',  #3

    'www.foobar.com/index.html',    #4
    'http://foobar.com/index.php',  #5
]

# remove protocol, leading 'www' and trailing '/index.$ext'
def normalize(url, _norm_pattern = re.compile(r'''^
                           (?: https?://)?
                           (?: www\.)?
                           (.+?)
                           (?: /index\. (?: s?html? | php | aspx? | jsp) )?
                           $''', re.VERBOSE | re.IGNORECASE)):
    return _norm_pattern.sub(r'\1', url.strip().lower()).rstrip('/')


class TestEquivalenceNoMerge(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence(normalize)

    def test_are_equivalent(self):
        self.assert_(self.eq.are_equivalent(*urls[0:3]))
        self.assert_(self.eq.are_equivalent(urls[4], urls[5]))
        self.assertFalse(self.eq.are_equivalent(urls[0], urls[2], urls[4]))

    def test_partitions(self):
        partitions = self.eq.partitions(urls[1:5])
        self.assert_(len(partitions) == 3 and
                     urls[1:3] in partitions and
                     urls[3:4] in partitions and
                     urls[4:5] in partitions)
        # before update
        self.assert_(self.eq.partitions() == [])
        # after update
        self.eq.update(*urls)
        partitions = self.eq.partitions()
        self.assert_(len(partitions) == 3 and
                     urls[:3] in partitions and
                     urls[3:4] in partitions and
                     urls[4:] in partitions)

    def test_partition(self):
        self.eq.update(*urls)
        self.assert_(self.eq.partition(urls[0]) == set(urls[:3]))
        self.assert_(self.eq.partition(urls[2]) == set(urls[:3]))
        self.assert_(self.eq.partition('www.uknown.com') == set())


class TestEquivalenceWithMerge(TestEquivalenceNoMerge):

    def setUp(self):
        self.eq = Equivalence(normalize)
        self.eq.merge(urls[3], urls[4])

    def test_are_equivalent(self):
        self.assert_(self.eq.are_equivalent(urls[3], urls[5]))
        self.assertFalse(self.eq.are_equivalent(urls[0], urls[4]))

    def test_partitions(self):
        partitions = self.eq.partitions(urls[1:5])
        self.assert_(len(partitions) == 2 and
                     urls[1:3] in partitions and
                     urls[3:5] in partitions)
        # before update
        self.assert_(self.eq.partitions() == [urls[3:5]])
        # after update
        self.eq.update(*urls)
        partitions = self.eq.partitions()
        self.assert_(len(partitions) == 2 and
                     urls[:3] in partitions and
                     urls[3:] in partitions)

    def test_partition(self):
        self.eq.update(*urls)
        self.assert_(self.eq.partition(urls[0]) == set(urls[:3]))
        self.assert_(self.eq.partition(urls[3]) == set(urls[3:]))
        self.assert_(self.eq.partition('www.uknown.com') == set())


if __name__ == '__main__':
    unittest.main()
