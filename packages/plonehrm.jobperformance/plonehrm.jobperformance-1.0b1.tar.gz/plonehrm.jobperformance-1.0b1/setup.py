from setuptools import setup, find_packages

version = '1.0'

setup(name='plonehrm.jobperformance',
      version=version,
      description="Adding Job performance reviews to plonehrm.",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='hrm',
      author='Jean-Paul Ladage',
      author_email='j.ladage@zestsoftware.nl',
      url='http://svn.plone.org/svn/collective/plonehrm.jobperformance',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonehrm'],
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
