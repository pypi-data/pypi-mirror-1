hexagonit.form
==============

Overview
--------

This package provides a drop-in replacement for the
``zope.formlib.form.Fields`` class that implements supporting the form
fields in the same manner that the Archetypes Schema class does.

Usage
-----

To use the orderable fields in your forms you need to use the
``hexagonit.form.orderable.OrderableFields`` instead of
``zope.formlib.form.Fields``.

After creating your form fields using this class the fields can be
moved around using the OrderableFields.moveField() method.

  >>> from hexagonit.form.orderable import OrderableFields
  >>> form_fields = OrderableFields(ISomeSchema)
  >>> form_fields.moveField("some_name", position="bottom")

See the doctests in ``orderable.txt`` for detailed examples on usage.
