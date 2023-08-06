# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: schema.py 5531 2008-01-24 13:37:55Z zagy $

import zope.schema.interfaces


def applySchemaData(context, schema, data, omit=()):
    """Apply `data` to `context` using `schema`."""
    omit = set(omit)
    for name in schema:
        if name in omit:
            continue
        field = schema[name]
        if not zope.schema.interfaces.IField.providedBy(field):
            continue
        value = data.get(name, field.default)
        setattr(context, name, value)
