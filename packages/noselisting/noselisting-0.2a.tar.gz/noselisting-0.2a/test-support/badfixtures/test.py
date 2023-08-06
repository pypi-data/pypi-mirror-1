import unittest

def setup():
    raise Exception()


def test_function():
    pass


class TestCase(unittest.TestCase):

    def setUp(self):
        raise Exception()

    def test(self):
        pass


class TestClass(object):

    def test(self):
        pass
