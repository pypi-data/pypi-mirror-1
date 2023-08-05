from setuptools import setup, find_packages

version = '0.1'

setup(name='collective.dtwidget',
      version=version,
      description="Munges the ATDateTime CalendarWidget into a formlib widget.  Plone only",
      long_description="""Takes the CalendarWidget shipped with Archetypes and Plone and displays the user input section as a formlib widget.  
      Use overrides.zcml to make this the default widget.  Correct functionality requires the CalendarWidget javascripts from core plone being accessible, as well as having
      ATContentTypes installed.  No unit tests yet, this is a proof of concept.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='formlib widget Datetime',
      author='Matthew Wilkes',
      author_email='matthew.wilkes@circulartriangle.eu',
      url='http://svn.plone.org/svn/plone/collective.dtwidget',
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
