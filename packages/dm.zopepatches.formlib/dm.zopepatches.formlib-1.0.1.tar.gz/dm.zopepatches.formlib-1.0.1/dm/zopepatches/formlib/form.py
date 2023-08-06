# Copyright(C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
"""'zope.formlib.form' improvements."""

from logging import getLogger
logger = getLogger('dm.zopepatches.formlib.form')


def failure(self, data, errors):
  """replacement for 'zope.formlib.form.Action.failure'.

  If 'failure_handler' is specified, call it (as 'Action.failure').
  Otherwise, call 'self.associate_errors_with_widgets'.
  """
  if self.failure_handler is not None:
    return self.failure_handler(self.form, self, data, errors)
  else: self.associate_errors_with_widgets(errors)

def associate_errors_with_widgets(self, errors):
  """propagate 'WidgetInputError' members of *errors* (a sequence)
  to the respective widget.
  """
  from zope.app.form.interfaces import WidgetInputError
  widgets = self.form.widgets
  for e in errors:
    if isinstance(e, WidgetInputError):
      f = e.field_name
      try:
        w = widgets[f]
      except KeyError:
        logger.error('could not find widget %s', f)
        continue
      # do not override an error because the widget set error is
      #  likely better
      if not w.error() and hasattr(w, 'setWidgetInputError'):
        w.setWidgetInputError(e)


def patch_action():
  """provide improved error hanlding.

  Unless an explicite failure handler is defined for the action,
  'WidgetInputError's are automatically propagated to the respective widget.

  Note: usually, 'widget.patch_widget' must be called as well in order to
  give the widgets a 'setWidgetInputError' method.
  """
  from patch import patch
  from zope.formlib.form import Action
  patch(Action, failure)
  patch(Action, associate_errors_with_widgets)
