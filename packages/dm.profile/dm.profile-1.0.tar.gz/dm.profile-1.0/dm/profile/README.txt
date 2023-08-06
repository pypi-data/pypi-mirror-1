==========
dm.profile
==========

"profile.Profile" improvement
-----------------------------

I started the implementation of this module in order to improve
the profiler's calibration using statistical methods.
Unfortunately, variance proved to be far too high and my calibration trials
did not converge even for large sample sets.
I had to abandon this approach.

The code is still there (in case anyone would like to look what I have
tried) but I do not use it.

"pstats.Stats" improvement
--------------------------

Beside the profiler's not so good calibration, I was not
satisfied with "pstats" format especially for the caller and callee analysis
and with its insistence to write to "stdout".

Therefore, I derived a new class ``Stats`` from ``pstats.Stats`` and added new
methods ``showStats``, ``showCallers`` and ``showCallees`` which
correspond to ``print_stats``, ``print_callers`` and ``print_callees``.
They write to a file set with ``setOutputFile`` (default ``sys.stdout``)
and use a different output format. For ``showCallers`` and ``showCallees``
it is much more readable than the format used by ``print_callers`` and
``print_callees``. I am not sure that this is also the case for the
format used for ``showStats`` versus ``print_stats``.

When you are using "Stats.print_callers" or "Stats.print_callees"
and find their output unreadable, then a switch to "dm.profile.Stats"
may be profitable for you.

The method ``showHeader`` outputs header information (with involved files,
top level functions, number of calls and profiled time).

