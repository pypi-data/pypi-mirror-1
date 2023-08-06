"""
Install numdifftools

Usage:

python setup.py install [, --prefix=$PREFIX]

python setup.py bdist_wininst

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
    version = '0.2',
    author="John D'Errico and Per A. Brodtkorb",
    author_email='woodchips@rochester.rr.com, Brodtkorb@frisurf.no',
    description = numdifftools.__doc__,
    license = "New BSD",
    url='',
    package_dir = {'numdifftools': ''},
    packages = ["numdifftools"],
    package_data = {'': packagedata},
    )
