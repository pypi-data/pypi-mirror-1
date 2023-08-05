"""Setup for ifrit package

$Id: setup.py,v 1.1 2007/02/09 14:54:38 tseaver Exp $
"""

try:
    from setuptools import setup
except ImportError, e:
    from distutils.core import setup

setup(name='ifrit',
      version='0.1',
      url='http://agendaless.com/Members/tseaver/software/ifrit',
      license='ZPL 2.1',
      description='XPath / ElementTree path adapters',
      author='Tres Seaver, Agendaless Consulting, Inc.',
      author_email='tseaver@agendaless.com',
      long_description='Define adapter factories based on XML paths',
      platform='Any',
      packages=['ifrit', 'ifrit.tests'],
      package_data = {'': ['*.txt', '*.zcml']},
      package_dir = {'': 'src'},
      install_requires=['zope.component',
                        'zope.configuration',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.schema',
                       ],
      extras_require={'speedy': ['lxml'],
                      'fallback': ['elementtree'],
                     },
      tests_require=['zope.app.testing',
                     'zope.testing.cleanup',
                     'zope.testing.doctest',
                    ],
      include_package_data = True,
      zip_safe = False,
      )

