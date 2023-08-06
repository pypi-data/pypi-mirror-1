from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc ="Interlude for Doctests provides an Interactive Console."
longdesc = """\
Provides an interactive shell aka console inside your doctest case.
    
The console looks exact like in a doctest-case and you can copy and paste
code from the shell into your doctest. It feels as you are in the test case 
itself. Its not pdb, it's a python shell. 

In your doctest you can invoke the shell at any point by calling::
        
    >>> interact( locals() )        

To make your testrunner interlude aware following is needed:

1) import interlude

2) suite = DocFileSuite( ..., globs=dict(interact=interlude.interact), ...) 

License
=======

`interlude` is copyright 2006-2009 by BlueDynamics Alliance, Klein & Partner KEG,
Austria. It is under the GNU Lesser General Public License (LGPLv3). 
http://opensource.org/licenses/lgpl-3.0.html

written by Jens Klein <jens@bluedynamics.com> 
""" 
setup(name='interlude',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 6 - Mature',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Topic :: Software Development :: Libraries :: Python Modules'        
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jens Klein',
      author_email='jens@bluedynamics.com',
      url='https://svn.bluedynamics.eu/svn/public/interlude/',
      license='LGPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
      ],
      extras_require={},
      entry_points="",
)