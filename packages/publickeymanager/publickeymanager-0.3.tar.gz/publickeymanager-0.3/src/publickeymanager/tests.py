import unittest

class TestServer(unittest.TestCase):
    def test_try(self):
        raise NotImplemented

def suite():
    s = unittest.TestSuite()
    ms = unittest.makeSuite
    s.addTest(ms(TestServer))
    return s
