from setuptools import setup, find_packages

version = '1.0.2'

setup(name='collective.validator.css',
      version=version,
      description="CSS Validator for collective.validator.base package",
      long_description="""This product is a CSS Validator for the collective.validator.base package.
          
This egg extend base functionalities and allow to validate all the css registered in portal_css.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Validator XHTML CSS',
      author='Andrea Cecchi',
      author_email='info@redturtle.net',
      url='https://svn.plone.org/svn/collective/collective.validator.css',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
