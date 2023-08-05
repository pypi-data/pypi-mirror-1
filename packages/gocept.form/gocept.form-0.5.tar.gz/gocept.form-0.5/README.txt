===========
gocept.form
===========

`gocept.form` provides some extended functionality for zope.formlib.

Destructive Actions
===================

Destructive actions allow marking actions that can potentially cause harm.
Those actions will be rendered as buttons and - on JavaScript-capable
platforms - be disabled by default. Additionally a checkbox is rendered that
allows enabling the corresponding button.


Grouped Fields
==============

gocept.form.grouped provides a very low-tech way of grouping schema fields
into field sets. The styling is applied only via CSS.

Changes
=======

0.5
---

- Added small function `applySchemaData` to apply data to an object according
  to a schema. This is useful in constructors or in add forms.

0.4
---

- Made grouped forms ignore missing fields.

0.3
---

- Added `destructive action` feature.


0.2
---

- Added support for grouping generic forms (subclass of zope.formlib.form.Form).


0.1
---

Initial release.
