# Copyright(C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
"""Fix 'zope.app.form.browser.itemswidgets.OrderMultiSelectionWidget'.

'OrderedMultiSelectWidget' accesses the field's context in
a surprising way triggering acquisition lookup (at least in Zope 2.10.x).
See http://dev.plone.org/plone/ticket/10267.

This is wrong not only because acquisition magic comes into play.
In addition, 'zope.formlib' supports a variety of ways how to provide
values for form fields which are not supported by looking at the content
object.
"""

def choices(self):
  """fixed 'choices' method: available {text, value} sequence."""
  values = self._getFormValue() or ()
  return [
    dict(text=self.textForValue(term), value=term.token)
    for term in self.vocabulary
    if term.value not in values
    ]

def selected(self):
  """fixed 'selected' method: selected {text, value} sequence."""
  values = self._getFormValue() or ()
  return [
    dict(text=self.textForValue(term), value=term.token)
    for term in map(self.vocabulary.getTerm, values)
    ]

def patch_OrderedMultiSelectWidget():
  from zope.app.form.browser.itemswidgets import OrderedMultiSelectWidget
  from patch import patch
  patch(OrderedMultiSelectWidget, choices)
  patch(OrderedMultiSelectWidget, selected)

