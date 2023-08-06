# vim: set expandtab ts=4 sw=4 filetype=python:

import unittest

import clepy.mattwilson as wmw

class TestMattWilson(unittest.TestCase):

    def test_draw_ascii_spinner(self):
        wmw.draw_ascii_spinner(0.001)


__id__ = "$Id: test_mattwilson.py 17 2009-08-03 01:29:56Z mw44118 $"
