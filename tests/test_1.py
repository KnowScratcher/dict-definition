import unittest
from unittest import TestCase
import sys

# setting path
sys.path.append('../dict_definition')
from get import Finder

TEST_WORD_1E = [
    'single',
    'double',
    'elaborate',
]

TEST_WORD_ES = [
    ('lay',8),
]


class TestFinder(TestCase):
    # def __init__(self, methodName: str = "runTest") -> None:
    #     super().__init__(methodName)

    def test_single_etymology(self):
        for word in TEST_WORD_1E:
            with self.subTest(word = word):
                fd = Finder(word)
                self.assertEqual(len(fd.find_etymologies()), 1)
    
    def test_multiple_etymologies(self):
        for word,count in TEST_WORD_ES:
            with self.subTest(word = word):
                fd = Finder(word)
                self.assertEqual(len(fd.find_etymologies()), count)
    

        
        
