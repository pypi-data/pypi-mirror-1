# -*- coding: latin-1 -*-
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Tools for schema field constraints."""


def _all(list):
    """Emulates Python 2.5's all() function."""
    return bool(len([x for x in list if x]))


def all(*constraints):
    return lambda value:_all([c(value) for c in constraints])
