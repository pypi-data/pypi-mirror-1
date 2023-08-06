"""
Install numdifftools

Usage:

python setup.py install [, --prefix=$PREFIX]

python setup.py bdist_wininst

PyPi upload:

python setup.py sdist bdist_wininst upload --show-response


"""
#!/usr/bin/env python
import os, sys

# make sure we import from this package, not an installed one:
sys.path.insert(0, os.path.join(''))
import numdifftools

if  __file__ == 'setupegg.py':
    # http://peak.telecommunity.com/DevCenter/setuptools
    from setuptools import setup, Extension
else:
    from distutils.core import setup

testscripts = [os.path.join('test', f)
               for f in os.listdir('test')
               if not (f.startswith('.') or f.endswith('~') or
                       f.endswith('.old') or f.endswith('.bak'))]
docs = [os.path.join('doc', f) for f in os.listdir('doc')]                       
packagedata = docs + testscripts                    
setup(
    name = "Numdifftools",
    version = '0.2.1',
    author="John D'Errico and Per A. Brodtkorb",
    author_email='woodchips at rochester.rr.com, Brodtkorb at frisurf.no',
    description = 'Solves automatic numerical differentiation problems in one or more variables.',
    long_description = numdifftools.__doc__,
    license = "New BSD",
    url='',
    maintainer='Per A. Brodtkorb',
    maintainer_email = 'Brodtkorb at frisurf.no',
    package_dir = {'numdifftools': ''},
    packages = ["numdifftools"],
    package_data = {'': packagedata},
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.5',
          'Topic :: Scientific/Engineering :: Mathematics',
          ],
    )
