from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "AnonymousCommenting", "version.txt")).read().strip()

setup(name='Products.AnonymousCommenting',
      version=version,
      description="Implements anonymous commenting within a Plone site",
      long_description=open("Products/AnonymousCommenting/README.txt").read() + "\n\n" +
                       open("Products/AnonymousCommenting/HISTORY.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python :: 2.4",
        ],
      keywords='',
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      url='http://weblion.psu.edu',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
