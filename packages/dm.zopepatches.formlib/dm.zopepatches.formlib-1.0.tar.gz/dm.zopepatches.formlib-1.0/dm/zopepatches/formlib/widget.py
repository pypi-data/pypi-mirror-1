# Copyright(C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
"""Patch 'zope.app.form.browser.widget'.
"""

def setWidgetInputError(self, error):
  """method for 'zope.app.form.browser.widget.BrowserWidget'."""
  self._error = error


def patch_widget():
  """path 'zope.app.form.browser.widget.BrowserWidget' to give it a 'setWidgetInputError'."""
  from zope.app.form.browser.widget import BrowserWidget
  from patch import patch
  patch(BrowserWidget, setWidgetInputError)
