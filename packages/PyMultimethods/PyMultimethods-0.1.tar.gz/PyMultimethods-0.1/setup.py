"""PyMultimethods: Multimethods for Python

PyMultimethods provides a pythonic library for implementing multimethods.  Multimethods are functions that exhibit polymorphic behaviour.  However, all of the function arguments are considered during dispatch.
"""

from distutils.core import setup

doclines = __doc__.split('\n')
summary = doclines[0]
description = '\n'.join(doclines[2:])

classifiers = ['Development Status :: 4 - Beta',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: GNU Affero General Public License v3',
               #'Operating System :: Os Independent',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Software Development :: Libraries :: Python Modules',
               ]

setup(name='PyMultimethods',
      version='0.1',
      description=summary,
      long_description=description,
      author='Nathan Davis',
      author_email='davisn90210@gmail.com',
      license='GNU AGPL, version 3',
      url='http://launchpad.net/pymultimethods',
      platforms=['any'],
      classifiers=classifiers,
      py_modules=['multidispatch'])
