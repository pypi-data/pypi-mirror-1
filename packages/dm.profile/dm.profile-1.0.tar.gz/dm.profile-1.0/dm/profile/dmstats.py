# Copyright (C) 2006 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: dmstats.py,v 1.1.1.1 2008/08/18 10:12:30 dieter Exp $
''''Stats' enhancements.

The module defines 'Stats' which inherits from Pythons 'Stats'
and enhances it by methods 'showCallees(funRe)', 'showCallers(funRe)'
and 'showStats(funRe)' which extracts information for functions
matched by the regular expression *funRe*.
This can make profile analysis significantly easier.
'''

from pstats import Stats as pStats, \
     func_get_function_name, func_std_string, \
     TupleComp
from sys import stdout
from re import compile

class Stats(pStats):
  _out = stdout

  def setOutputFile(self, file):
    self._out = file

  def showCallees(self, *amount):
    msg, fs = self._selectFunctions(amount)
    self._print(msg)
    for f in fs: self._showCallees(f); self._print('\n')

  def showStats(self, *amount):
    msg, fs = self._selectFunctions(amount)
    self._print(msg)
    self._print("\n%5s - %21s - %21s - Stdname\n"
                % ("Calls", "Internal Time", "Cumulative Time")
                )
    for f in fs: self._showStats(f)

  def showCallers(self, *amount):
    msg, fs = self._selectFunctions(amount)
    self._print(msg)
    for f in fs: self._showCallers(f); self._print('\n')

  def showHeader(self):
    """output heading information (files, statistics)."""
    if self.files:
      for filename in self.files: self._print(filename + '\n')
      self._print('\n')
    indent = ' ' * 9 
    for func in self.top_level:
      self._print(indent + func_get_function_name(func) + "\n")
    self._print(indent + `self.total_calls` + " function calls")
    if self.total_calls != self.prim_calls:
      self._print(" (%d primitive calls)" % self.prim_calls)
    self._print(" in %.3f seconds" % self.total_tt + "\n")

  def _selectFunctions(self, amount):
    if self.fcn_list:
      l = self.fcn_list
      msg = "   Ordered by: " + self.sort_type + '\n'
    else:
      l = self.stats.keys()
      msg = "   Unordered\n"
    for sel in amount:
      l, msg = self.eval_print_amount(sel, l, msg)
    return msg, l

  def _showCallees(self, f):
    self._showStats(f)
    self.calc_callees()
    callees = self.all_callees.get(f)
    if not callees: return
    self._showSortedChildren(callees, 'of')

  # fix "sort_arg_dict_default" to distinguish between "calls" and "pcalls"
  sort_arg_dict_default = pStats.sort_arg_dict_default.copy()
  sort_arg_dict_default['pcalls'] = (sort_arg_dict_default['pcalls'][0], 'primary call count')

  def _showSortedChildren(self, children, tag):
    stats = self.stats; format = self._formatFunction
    # normalized list "nl" consists of tuples
    # see "sort_stats", for details
    #  local call count -- corresponds to "pcalls"
    #  global call count -- corresponds to "calls"
    #  (global) internal time
    #  (global) cumulative time
    #  file, line, name
    #  stdname
    #  function triple
    nl = []
    for cf, calls in children.iteritems():
      (cc, nc, tt, ct, callers) = stats[cf]
      nl.append((calls, nc, tt, ct) + cf + (func_std_string(cf), cf))
    if self.fcn_list:
      # sort the children list
      # reverse engineer "sort_tuple" (see "sort_stats" for details)
      sort_arg_defs = self.get_sort_arg_defs(); sort_tuple = ()
      sort_specs = self.sort_type.split(', ')
      for s in sort_specs:
        for dt, ds in sort_arg_defs.itervalues():
          if s == ds: sort_tuple += dt; break
        else: raise ValueError('sort order not found: ' + str(s))
      nl.sort(TupleComp(sort_tuple).compare)
    for (calls, nc, tt, ct, module, line, fn, std, cf) in nl:
      self._print('\t%4dc\t(%s %4dc in %8.3fs)\t%s\n'
                  % (calls, tag, nc, ct, format(cf), )
                  )

  def _showCallers(self, f):
    self._showStats(f)
    self._showSortedChildren(self.stats[f][4], "from")
      
  # Note: should you override this, you probably should also
  #  override "eval_print_amount" to let the "stdname" regex correctly work
  def _formatFunction(self, ft):
    return func_std_string(ft)

  def _showStats(self, ft):
    s = self.stats[ft]
    self._print('%4dc - %8.3fs %8.3fs/c - %8.3fs %8.3fs/c - %s\n' % (
      s[1], s[2], s[2]/s[1], s[3], s[3]/s[1], self._formatFunction(ft),
      )
                )

  def _print(self, txt):
    self._out.write(txt)
