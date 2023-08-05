#! /usr/bin/env python
"""This is the installation script for the EvoGrid libraries

setuptools is required
"""


try:
    from setuptools import setup, find_packages
except ImportError:
    print 'setuptools could not be found: please run "python ez_setup.py"'
    print 'to get the latest version'
    import sys; sys.exit(1)

setup(name='evogrid',
      version='0.1.0',
      author='Olivier Grisel',
      author_email='olivier.grisel@ensta.org',
      url='http://champiland.homelinux.net/evogrid/doc',
      download_url='http://cheeseshop.python.org/pypi/evogrid',
      description='Distributed Evolutionary Computation framework',
      long_description="""\
Componentized Machine Learning system whose design is mainly based on
Evolutionary Computation ideas, especially Memetic Computing: building blocks
are ``Replicators`` that evolve in a potentially networked environment.

The goal of EvoGrid is to provide a pluggable framework (based on the Zope
Component Architecture) and reuse as much as possible existing ML algorithms
implementations (either in Python or other language as long as the can be
wrapped into a pythonic component).

The project is currently at an early development stage providing only
implementation for base evolutionary components (not GRID / networking support
yet).

For more details of what is included and what is planned, please refer to the
launchpad project page at https://launchpad.net/products/evogrid .

To get started with evogrid, please read the HTML rendered doctests published on
the homepage and especially the main tutorial at:
      http://champiland.homelinux.net/evogrid/doc/components_overview.html
""",
      license='GNU GPL v2',
      packages = find_packages('src'),
      package_dir = {'':'src'},
      package_data = {'': ['*.txt']},
      install_requires=["zope.interface", "zope.component", "numpy",
                        "python-memcached"],
      # XXX: matlotlib not required yet
      # XXX: scipy is not in the list cause not yet installable with
      # easy_install
      zip_safe=False, # make it true by using pkg_resources for the doctests
      test_suite= 'src.evogrid.tests.evogrid_test_suite',
      tests_require=["zope.testing", "trace2html"],
      dependency_links=[
        "http://download.zope.org/distribution",
        "ftp://ftp.tummy.com/pub/python-memcached/python-memcached-1.31.tar.gz",
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      )

try:
    import scipy
except ImportError:
    print "You should now install 'scipy' manually from:"
    print " http://www.scipy.org/"
    print "or by using the version of your distribution"
