from setuptools import setup, find_packages
import os

__name__ = 'wsapi4plone.core'
__version__ = '0.1'

setup(name=__name__,
      version=__version__,
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      description="A Web Services API for Plone.",
      long_description=open('README.txt').read() + "\n\n" +
                       open('USAGE.txt').read() + "\n\n" +
                       # open(os.path.join('wsapi4plone', 'core', 'service.txt')).read() + "\n\n" +
                       open('CHANGES.txt').read() + "\n\n" +
                       open('CONTACT.txt').read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=["Framework :: Plone",
                   "Framework :: Zope2",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.4",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Intended Audience :: Developers",
                   # "Development Status :: 3 - Alpha",
                   ],
      keywords='wsapi, api, xmlrpc, weblion',
      url='https://weblion.psu.edu/trac/weblion/wiki/WebServicesApiPlone',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'bootstrap.py']),
      namespace_packages=['wsapi4plone'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.traversing',
                                  ]),
      install_requires=['setuptools',
                        # If versions of Plone < 3.2 want to be used, the Plone egg dependency
                        # can't be included (e.g Plone 3.1.7)
                        # Can not include this line, because the Plone egg is version >= 3.2
                        # 'plone',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      include_package_data=True,
      zip_safe=False,
      )
