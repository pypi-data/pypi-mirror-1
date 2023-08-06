from setuptools import setup, find_packages
import os.path


def get_file_contents_from_main_dir(filename):
    file_path = os.path.join('plonehrm', 'jobperformance', filename)
    this_file = open(file_path)
    contents = this_file.read().strip()
    this_file.close()
    return contents

version = get_file_contents_from_main_dir('version.txt')
history = get_file_contents_from_main_dir('HISTORY.txt')
readme = get_file_contents_from_main_dir('README.txt')
long = "%s\n\n\n%s" % (readme, history)


setup(name='plonehrm.jobperformance',
      version=version,
      description="Job performance interviews for Plone HRM.",
      long_description=long,
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
          'collective.autopermission',
          'Products.plonehrm>=2.7',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
