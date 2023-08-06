from setuptools import setup, find_packages
import os

setup(name='wsapi4plone.core',
    version='0.1a2',
    author='WebLion Group, Penn State University',
    author_email='support@weblion.psu.edu',
    description="A Web Services API for Plone.",
    long_description=open('README.txt').read() + "\n" +
                   open("CHANGES.txt").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        ],
    keywords='wsapi api xmlrpc weblion',
    url='https://weblion.psu.edu/trac/weblion/wiki/WebServicesApiPlone',
    license='GPL',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['wsapi4plone'],
    extras_require = dict(test=['zope.app.testing',
                              'zope.testing',
                              'zope.traversing',
                              ]),
    install_requires=[
      'setuptools',
      'plone>=3.2', # plone 2.5?
      # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    include_package_data=True,
    zip_safe=False,
    )
