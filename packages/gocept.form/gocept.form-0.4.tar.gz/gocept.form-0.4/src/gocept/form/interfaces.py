# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: interfaces.py 5091 2007-08-22 14:25:17Z zagy $

import zope.interface
import zope.schema

class IFieldGroup(zope.interface.Interface):

    title = zope.schema.TextLine(title=u"Widget Group Title")

    css_class = zope.schema.TextLine(
        title=u"CSS class to apply to the group")

    widgets = zope.schema.List(
        title=u"Widges of this group",
        description=u"Will be filled by form")

    def get_field_names():
        "Return list of field names."


class IRemainingFields(IFieldGroup):
    """Marker interface for a fieldgroup which contains all remaining fields.

    Remaining fields are fields which are not noted in any other field group.

    """

    def get_field_names():
        """Returns None."""


class IGroupedForm(zope.interface.Interface):

    field_groups = zope.schema.List(
        title=u"Field groups to display",
        value_type=zope.schema.Object(IFieldGroup))
