# -*- coding: latin-1 -*-
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Additional actions."""

import zope.formlib.form
import zope.formlib.namedtemplate

class DestructiveAction(zope.formlib.form.Action):
    pass


@zope.formlib.namedtemplate.implementation(DestructiveAction)
def render_destructive_action(self):
    button = zope.formlib.form.render_submit_button(self)()
    if button == '':
        return ''

    # Extend the button with a check box that is synchronized with the
    # 'active' status of the button.

    additional = """
        <script type="text/javascript">
        document.getElementById('%s').disabled = true;
        </script>

        <label>
            <input
            type="checkbox" 
            id="%s" 
            onChange="document.getElementById('%s').disabled = !this.checked"/> Unlock &quot;%s&quot; button</label>

    """ % (self.__name__, self.__name__ + '.unlock', self.__name__, self.label)
    # XXX: the label should be translated.

    return button + additional


class destructive_action(zope.formlib.form.action):
    """Decorator to create destructive actions in form views."""

    def __call__(self, success):
        action = DestructiveAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action
