This package allows to work around
problems/weaknesses in ``zope.formlib`` and the associated widgets in 
``zope.app.form.browser``.

The package consists of various modules described below.

To use the package in your application, you import some of its
patch functions (mentioned below) and call them during the startup
of your application.

I hope that corresponding patches will sooner or later appear in the
standard Zope code and make this package obsolete.


form
----

Together with ``widget``, this module is destined to work
around http://dev.plone.org/plone/ticket/10264.

``zope.formlib`` distinguishes between widget related errors
and other (more global) errors. If a widget itself detects a
widget related error (usually because a restriction for the
associated field fails), it sets its error condition.
This error condition is usually used to highlight the widget containing an
error and to provide information about this error.
However, if the widget related error is not detected by the
widget itself, the error is not associated with the widget and
important information may be missing.

The function ``patch_action()`` in module ``form`` enhances
``zope.formlib.form.Action`` by an additional method
``associate_errors_with_widgets`` and redefines its
``failure`` method to call it unless an explicit failure handler is specified.
This provides for automatic error association with the widgets
in the standard case.

``associate_errors_with_widgets`` tries to associate
``zope.app.form.interfaces.WidgetInputError`` with
the corresponding widget. For this purpose, the widget
must have a ``setWidgetInputError`` method.
By default widgets lack this method. However ``widget.patch_widget()``
can be used to define it. Therefore, ``form.patch_action()``
and ``widget.patch_widget()`` are usually used together.


widget
------
Together with ``form``, this module is destined to work
around http://dev.plone.org/plone/ticket/10264.

Its ``patch_widget()`` enhances
``zope.app.form.browser.widget.BrowserWidget`` (the base class for
``zope.app.form`` widgets) by defining the method ``setWidgetInputError``.
The method allows external code to set an error condition on the widget.

``setWidgetInputError`` is used by the error handling implemented
by the ``form`` module. Therefore, ``widget.patch_widget()`` is usually
used together with ``form.patch_action()``.


multiselection
--------------

This module is destined to work around
http://dev.plone.org/plone/ticket/10267.

Its ``patch_OrderedMultiSelectWidget()``
fixes ``zope.app.form.browser.itemswidgets.OrderedMultiSelectWidget``.

