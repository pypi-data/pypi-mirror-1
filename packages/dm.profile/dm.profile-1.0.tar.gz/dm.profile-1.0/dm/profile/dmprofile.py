# Copyright (C) 2006-2007 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: dmprofile.py,v 1.1.1.1 2008/08/18 10:12:30 dieter Exp $
'''profile enhancements.'''

from profile import Profile

class Profile(Profile):
  _inherited_calibrate_inner = Profile._calibrate_inner

  def measure_error(self, m=2000):
    '''similar to '_calibrate_inner', but

     * use our timer and bias

     * bring the measured time in the order of the profiled time
       to counter effects of the limited resolution
       ("clock" has very bad resolution on "Linux")

     * do not print but return the information in a dictionary.

     * avoid additional calls
    '''
    gt = self.get_time

    def f1(n):
      i = 0
      while i < n: i += 1

    def f(m, f1=f1):
      i = 0
      while i < m:
        i += 1
        f1(1000)

    f(2) # warm up the cache

    # measure no-profile execution
    s = gt(); f(m); npt = gt() - s

    # measure profile execution
    p = self.__class__(self.timer, self.bias) # a new profiler like us
    s = gt(); p.runcall(f, m); pt = gt() - s
    
    # determine reported time
    calls = 0; reported = 0.0
    for (filename, line, funcname), (cc, ns, tt, ct, callers) in \
            p.timings.items():
      if funcname in ("f", "f1"): calls += cc; reported += tt

    if calls != m+1:
      raise ValueError('internal error: unexpected number of calls: %d != %d'
                       % (m+1, calls)
                       )

    return {
      'real_time':npt,
      'reported_time':reported,
      'profile_time':pt,
      'error_per_event':(reported-npt) / 2.0 / calls,
      }

  def do_calibrate(self, m=2000, iterate=5):
    '''adjust our bias based on error measurement.

    Note that due to limited time resolution and other non deterministic
    effects, the measured error varies.
    We therefore make several measurements and take the mean value.
    '''
    error = 0.0
    for i in range(iterate):
      error += self.measure_error(m)['error_per_event']
    self.bias += error / iterate
    
