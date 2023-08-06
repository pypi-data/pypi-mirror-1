# Author: John Salvatier <jsalvati@u.washington.edu>, 2009.
import setuptools


DISTNAME            = 'scikits.bvp_solver'
DESCRIPTION         = "Python package for solving two-point boundary value problems"
LONG_DESCRIPTION    ="""
        bvp_solver is a Python package for solving two-point boundary value problems that wraps
        BVP_SOLVER (see http://cs.stmarys.ca/~muir/BVP_SOLVER_Webpage.shtml). It is currently fully
        working and mostly complete, but it is still being documented and improved. A quick start
        guide and some example can be found at: http://bvp-solver.wikidot.com. If you have questions
        or suggestions send an e-mail to the mailing list or me.

        bvp_solver is intended to eventually be BSD licensed so that it may be included in SciPy,
        but BVP_SOLVER currently relies on COLROW which is subject to ACM license which prohibits
        free commercial use. One of the creators of the BVP_SOLVER Fortran code has informed me that
        he believes he can create a free algorithm that accomplishes the same thing.

        To join the mailing list send an e-mail to scikits-bvp_solver+subscribe@googlegroups.com
        """
MAINTAINER          = 'John Salvatier'
MAINTAINER_EMAIL    = "jsalvati@u.washington.edu"
URL                 = "http://bvp-solver.wikidot.com"
LICENSE             = "BSD but uses COLROW which cannot be used in commercial packages without contacting the ACM."
VERSION             = "0.2.5"

classifiers =  ['Development Status :: 3 - Alpha',
                'Programming Language :: Python',
                'License :: Free for non-commercial use',
                'License :: OSI Approved :: BSD License',
                'Intended Audience :: Science/Research',
                'Topic :: Scientific/Engineering',
                'Topic :: Scientific/Engineering :: Mathematics',
                'Operating System :: OS Independent']

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
                           long_description = LONG_DESCRIPTION)

    config.add_data_files('scikits/__init__.py')
    config.add_extension('bvp_solverf',
                         sources=['scikits/bvp_solver/lib/bvp_interface.pyf',
                                  'scikits/bvp_solver/lib/BVP_LA.f',
                                  'scikits/bvp_solver/lib/BVP_M.f90',
                                  'scikits/bvp_solver/lib/BVP_INTERFACE.f90'])

    config.add_data_files('scikits/bvp_solver/examples/*.*')
    config.add_data_files('scikits/bvp_solver/lib/BVP_SOLVER_License.txt')
    config.add_data_files('scikits/bvp_solver/lib/BVP_LA_LicenseInfo.txt')
    return config



if __name__ == "__main__":

    from numpy.distutils.core import setup
    setup(configuration=configuration,
        packages = setuptools.find_packages(),
        include_package_data = True,
        platforms = ["any"],
        install_requires=["numpy >= 1.2"],
        tests_require = ['nose >= 0.10.3',],
        test_suite='nose.collector',
        zip_safe = True,
        classifiers =classifiers)
