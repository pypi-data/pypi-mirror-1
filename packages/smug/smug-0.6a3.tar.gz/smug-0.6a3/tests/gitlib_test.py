#!/usr/bin/env python

import doctest
import gitlib


doctest.testmod(gitlib.objects)
doctest.testmod(gitlib.repo)
doctest.testmod(gitlib.index)
doctest.testfile('../docs/gitlib.txt')


# vim: et sw=4 sts=4
