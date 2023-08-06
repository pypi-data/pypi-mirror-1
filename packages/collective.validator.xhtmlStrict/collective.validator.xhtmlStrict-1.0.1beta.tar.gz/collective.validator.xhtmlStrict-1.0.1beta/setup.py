from setuptools import setup, find_packages

version = '1.0.1'

setup(name='collective.validator.xhtmlStrict',
      version=version,
      description="XHTML Strict Validator for collective.validator.base",
      long_description="""
This product is an XHTML Strict Validator for the collective.validator.base package.
    
This egg extends base functionalities and allows to validate all the portal types selected, or a single page with the XHTML Strict type.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Validator XHTMLStrict',
      author='Andrea Cecchi',
      author_email='info@redturtle.net',
      url='https://svn.plone.org/svn/collective/collective.validator.xhtmlStrict',
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
