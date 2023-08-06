'''
Created on Oct 24, 2009

# Author: John Salvatier <jsalvati@u.washington.edu>, 2009.
'''
from setuptools import setup, Extension
from Cython.Distutils import build_ext


DISTNAME            = 'pymcdream'
DESCRIPTION         = "Implements DREAM in Python based on PyMC"
LONG_DESCRIPTION    ="""
                    Based on the algorithm in 
                    J.A. Vrugt, C.J.F. ter Braak, C.G.H. Diks, D. Higdon, B.A. Robinson, and J.M. Hyman: Accelerating Markov chain Monte Carlo simulation by differential evolution with self-adaptive randomized subspace sampling.  International Journal of Nonlinear Sciences and Numerical Simulation, 2008, In Press.
                    """
MAINTAINER          = 'John Salvatier'
MAINTAINER_EMAIL    = "jsalvati@u.washington.edu"
URL                 = "pypi.python.org/pypi/dream"
LICENSE             = "BSD"
VERSION             = "0.1.0"

classifiers =  ['Development Status :: 4 - Beta',
                'Programming Language :: Python',
                'License :: OSI Approved :: BSD License',
                'Intended Audience :: Science/Research',
                'Topic :: Scientific/Engineering',
                'Topic :: Scientific/Engineering :: Mathematics',
                'Operating System :: OS Independent']

if __name__ == "__main__":

    setup(name = DISTNAME,
          version = VERSION,
        maintainer  = MAINTAINER,
        maintainer_email = MAINTAINER_EMAIL,
        description = DESCRIPTION,
        license = LICENSE,
        url = URL,
        long_description = LONG_DESCRIPTION,
        packages = ['pymcdream'],
        classifiers =classifiers,
        install_requires=["pymc >= 2.0", "numpy >= 1.2",'scipy >= 0.7'],
        cmdclass = {'build_ext': build_ext},
        ext_modules = [Extension("pymcdream.rand_no_replace", ["pymcdream/rand_no_replace.pyx"])])

