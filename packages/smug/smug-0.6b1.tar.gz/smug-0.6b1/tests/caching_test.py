#!/usr/bin/env python

import doctest
from smug import load


doctest.testmod(load)
doctest.testfile('../docs/caching.txt')


# vim: et sw=4 sts=4
