# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 987 2009-01-31 16:38:00Z mac $

import doctest

def test_all():
    return doctest.DocFileSuite('README.txt')
