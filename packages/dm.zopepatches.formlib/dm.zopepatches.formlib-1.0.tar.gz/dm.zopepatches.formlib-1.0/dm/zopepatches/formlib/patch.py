# Copyright(C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
"""Patch utility."""
from logging import getLogger
log = getLogger('dm.zopepatches.formlib').info


def patch(target, function, name=None):
  """patch *target* with *function* for *name*.

  Prevent multiple patching.
  Make previous object available under *name* with suffix '_dmzpfl_patched_'.
  Log patching.
  """
  if name is None: name = function.func_name
  tag = name + '_dmzpfl_patched_'
  if hasattr(target, tag): return # already patched
  setattr(target, tag, getattr(target, name, None))
  setattr(target, name, function)
  log('patched %s, attribute %s' % (target, name))

