from django.test import TestCase

from converters.boundaries import BBox


class TestBBox(TestCase):
    def setUp(self):
        self.boundary = BBox(west=0, south=0, east=0, north=0)

    def test_init_complains_when_parameters_are_missing(self):
        self.assertRaises(TypeError, BBox, west=0, south=0, east=0)
        self.assertRaises(TypeError, BBox, west=0, south=0, north=0)
        self.assertRaises(TypeError, BBox, west=0, east=0, north=0)
        self.assertRaises(TypeError, BBox, south=0, east=0, north=0)
        self.assertRaises(TypeError, BBox, north=0)
        self.assertRaises(TypeError, BBox, east=0)
        self.assertRaises(TypeError, BBox, south=0)
        self.assertRaises(TypeError, BBox, west=0)

    def test_initializing_works_if_all_given_parameters_are_set(self):
        # shouldn't raise an error
        BBox(west=0, south=0, east=0, north=0)
