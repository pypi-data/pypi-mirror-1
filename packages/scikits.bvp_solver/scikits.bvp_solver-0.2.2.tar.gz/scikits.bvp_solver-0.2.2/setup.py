# Author: John Salvatier <jsalvati@u.washington.edu>, 2009.
try: import setuptools
except ImportError: pass

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)
    config.add_subpackage('scikits')
    config.add_subpackage('scikits.bvp_solver')
    config.add_subpackage('scikits.bvp_solver.tests')
    config.add_subpackage('scikits.bvp_solver.tests.test_examples')

    return config


package_data = {'scikits.bvp_solver' : ['examples/*']}



if __name__ == "__main__":


    classifiers ="""\
    Development Status :: 2 - Pre-Alpha
    Programming Language :: Python
    License :: Free for non-commercial use
    Intended Audience :: Science/Research
    Topic :: Scientific/Engineering
    Topic :: Scientific/Engineering :: Mathematics
    Operating System :: Microsoft :: Windows
    Operating System :: Unix"""


    from numpy.distutils.core import setup
    setup(
        name='scikits.bvp_solver',
        author="John Salvatier",
        author_email="jsalvati@u.washington.edu",
        version="0.2.2",
        url="http://bvp-solver.wikidot.com",
        license="BSD but uses COLROW which cannot be used in commercial packages without contacting the ACM.",
        description = "Boundary Value Problem Solver. Primarily a wrapper for BVP_SOLVER",
        classifiers =filter(None, classifiers.split("\n")),
        long_description=
        """
        bvp_solver if a boundary value problem solver for Python that wraps BVP_SOLVER
        (see http://cs.stmarys.ca/~muir/BVP_SOLVER_Webpage.shtml). It is currently fully
        working, but in active development. See the doc strings to see how to run the solver.
        The interface is somewhat different than BVP_SOLVER, but I am experimenting. If you
        have comments about this, please email me. bvp_solver is eventually intended to be BSD
        licensed so that it can eventually be merged with SciPy, but the Fortran code that runs
        it currently relies on COLROW which is subject to ACM license which prohibits free
        commercial use. One of the creators of the BVP_SOLVER Fortran code has informed me
        that he believes he can find a free algorithm that accomplishes the same thing.

        A quick start guide and some example can be found here: http://bvp-solver.wikidot.com
        """,
        platforms = ["any"],
        install_requires=["numpy >= 1.2", 'Nose'],
        configuration=configuration,
        test_suite='nose.collector',
        package_data = package_data
        )
