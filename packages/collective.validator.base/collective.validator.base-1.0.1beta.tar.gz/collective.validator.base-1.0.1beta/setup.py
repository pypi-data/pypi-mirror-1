from setuptools import setup, find_packages

version = '1.0.1'

setup(name='collective.validator.base',
      version=version,
      description="A Plone pages validator",
      long_description="""
ValidationTool is a web validator for Plone 3. It validate all the pages of the plone site that we want.
    
This package is a base-tool that set some option fields and needs plugin-packages to do the effective validation.
    
Each plugin allows to set a different type of validation (like Css,xhtml Strict or Transitional).
    
Every package has some tests and is also translated in italian.
    
The base-tool is an installing product, and the plugins needs only to  be placed in the "src" directory and registered in buiildout.cfg.
    
Once installed the package with quick installer, you can see it and set its fields in site setup->additional products.
    
If you click it,you go in a page that allows us to see the report list of validations, or configure our tool.
    
It is also possible validate a single page by clicking on "validate XHTML some_validator" link at the bottom, if the page belongs to
the selected types.
    
An other functionality is the remote validation. It allows to run a validation of the site using "url_of_the_site/remote_validator".
    
This functionality can be used for example if you want to schedule a periodical validation with probrams like "cron".
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
      author_email='andrea.cecchi@redturtle.net',
      url='https://svn.plone.org/svn/collective/collective.validator.base',
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
