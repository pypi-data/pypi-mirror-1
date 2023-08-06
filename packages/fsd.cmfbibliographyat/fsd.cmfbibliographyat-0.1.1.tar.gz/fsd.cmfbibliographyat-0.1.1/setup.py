from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='fsd.cmfbibliographyat',
      version=version,
      description="A simple integration of CMFBibliographyAT with FacultyStaffDirectory",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='https://weblion.psu.edu/svn/weblion/weblion/fsd.cmfbibliographyat/trunk/fsd/cmfbibliographyat',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['fsd'],
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
