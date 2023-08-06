# Author: John Salvatier <jsalvati@u.washington.edu>, 2009.
import setuptools


DISTNAME            = 'scikits.bvp_solver'
DESCRIPTION         = "Boundary Value Problem Solver. Primarily a wrapper for BVP_SOLVER"
LONG_DESCRIPTION    ="""
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
        """
MAINTAINER          = 'John Salvatier'
MAINTAINER_EMAIL    = "jsalvati@u.washington.edu"
URL                 = "http://bvp-solver.wikidot.com"
LICENSE             = "BSD but uses COLROW which cannot be used in commercial packages without contacting the ACM."
DOWNLOAD_URL        = URL
VERSION             = "0.2.4"

classifiers =  ['Development Status :: 2 - Pre-Alpha',
                'Programming Language :: Python',
                'License :: Free for non-commercial use',
                'Intended Audience :: Science/Research',
                'Topic :: Scientific/Engineering',
                'Topic :: Scientific/Engineering :: Mathematics',
                'Operating System :: Microsoft :: Windows',
                'Operating System :: Unix']

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(DISTNAME, parent_package, top_path,
                           namespace_packages = ['scikits'],
                           version = VERSION,
                           maintainer  = MAINTAINER,
                           maintainer_email = MAINTAINER_EMAIL,
                           description = DESCRIPTION,
                           license = LICENSE,
                           url = URL,
                           download_url = DOWNLOAD_URL,
                           long_description = LONG_DESCRIPTION)

    config.add_data_files('scikits/__init__.py')
    config.add_extension('bvp_solverf',
                         sources=['scikits/bvp_solver/lib/bvp_interface.pyf',
                                  'scikits/bvp_solver/lib/BVP_LA.f',
                                  'scikits/bvp_solver/lib/BVP_M.f90',
                                  'scikits/bvp_solver/lib/BVP_INTERFACE.f90'])

    config.add_data_files('scikits/bvp_solver/examples/*.*')
    return config



if __name__ == "__main__":

    from numpy.distutils.core import setup
    setup(configuration=configuration,
        packages = setuptools.find_packages(),
        include_package_data = True,
        platforms = ["any"],
        install_requires=["numpy >= 1.2", 'Nose'],
        test_suite='nose.collector',
        zip_safe = True,
        classifiers =classifiers)
