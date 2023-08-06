import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

longdescription=("""
This product is an XHTML Strict Validator for the collective.validator.base package.
    
This egg extends base functionalities and allows to validate all the portal types selected, or a single page with the XHTML Transitional type.
"""
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('collective/validator/xhtmlTransitional/HISTORY.txt')+
    'Download\n'
    '********\n'
    )


version = '1.0.2'

setup(name='collective.validator.xhtmlTransitional',
      version=version,
      description="XHTML transitional Validator for collective.validator.base",
      long_description=longdescription,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Validator XHTMLTransitional',
      author='Andrea Cecchi',
      author_email='andrea.cecchi@redturtle.net',
      url='https://svn.plone.org/svn/collective/collective.validator.xhtmlTransitional',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective','collective.validator'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
