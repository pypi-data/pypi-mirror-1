"""qq.py -- Q-Q plots to test mtrand's distributions
"""

import scipy as sp
from matplotlib import pylab as pl

import mtrand

rs = mtrand._rand

class DistTester(object):
    def __init__(self, mtfunc, spdist):
        self.mtfunc = mtfunc
        self.spdist = spdist

    def qq(self, size, mtargs, spargs):
        vals = self.mtfunc(size=size, *mtargs)
        vals = sp.sort(vals)
        x = sp.linspace(0.0, 1.0, size)
        y = self.spdist.cdf(vals, *spargs)
        pl.ioff()
        pl.clf()
        pl.plot(x, y, 'k-')
        pl.plot([0,1], [0,1], 'k:')
        pl.show()
        pl.ion()

exponential = DistTester(rs.exponential, sp.stats.expon)
normal = DistTester(rs.normal, sp.stats.norm)
standard_normal = DistTester(rs.standard_normal, sp.stats.norm)
gamma = DistTester(rs.gamma, sp.stats.gamma)
standard_gamma = DistTester(rs.standard_gamma, sp.stats.gamma)
uniform = DistTester(rs.uniform, sp.stats.uniform)
beta = DistTester(rs.beta, sp.stats.beta)
f = DistTester(rs.f, sp.stats.f)
noncentral_f = DistTester(rs.noncentral_f, sp.stats.ncf)
chisquare = DistTester(rs.chisquare, sp.stats.chi2)
noncentral_chisquare = DistTester(rs.noncentral_chisquare, sp.stats.ncx2)
binomial = DistTester(rs.binomial, sp.stats.binom)
negative_binomial = DistTester(rs.negative_binomial, sp.stats.nbinom)
poisson = DistTester(rs.poisson, sp.stats.poisson)

# Examples:
# beta.qq(1000, (2., 3.), (2., 3.))
# gamma.qq(10000, (15, 10), (15, 0, 10))  # scipy.stats.gamma has a loc
                                          # parameter that we need to ignore
# ... etc. Only integer values for size are permitted.

