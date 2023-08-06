from timeit import Timer
import numpy as np
import numexpr as ne

p, q = 3.1, 5.4  # constants

for N in (1e3, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6):  # size of arrays
    M = 20 * int(1e6 / N)   # number of repetitions for times
    pi = np.arange(N)

    print " *** Times for arrays with %s elements *** " % int(N)

    Tnp = Timer("p*pi[1:] + q*np.sin(pi[:-1])",
                "from __main__ import np,pi,p,q")
    tnp = min(Tnp.repeat(3,M))
    print "NumPy time:", round(tnp,3),
    print "\ttime per evaluation:", round(tnp/M*1e3,3), "ms"

    Tne = Timer("pi1, pi2 = pi[1:], pi[:-1]; ne.evaluate('p*pi1 + q*sin(pi2)')",
                "from __main__ import pi,p,q,ne;ne.set_vml_num_threads(1)")
    tne = min(Tne.repeat(3,M))
    print "Numexpr time:", round(tne,3),
    print "\ttime per evaluation:", round(tne/M*1e3,3), "ms"
