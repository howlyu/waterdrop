import unittest
from unittest import TestCase


class TestCommand(TestCase):

    @unittest.SkipTest
    def test_start(self):
        pass

    @unittest.SkipTest
    def test_stop(self):
        pass

    def test_list(self):
        self.fail()

    def test_cancel(self):
        self.fail()

    def test_create(self):
        self.fail()
