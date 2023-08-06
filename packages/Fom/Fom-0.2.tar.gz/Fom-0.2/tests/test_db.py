import unittest

from fom.db import FluidDB


class TestDB(unittest.TestCase):

    def test_default(self):
        db = FluidDB('http://sandbox.fluidinfo.com')
        self.assertEquals(db.base_url, 'http://sandbox.fluidinfo.com')

    def test_call(self):
        db = FluidDB('http://sandbox.fluidinfo.com')
        r = db('GET', '/users/aliafshar')
        self.assertEquals(r.value['name'], u'aliafshar')


if __name__ == '__main__':
    unittest.main()
