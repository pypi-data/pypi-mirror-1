from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.idashboard',
      version=version,
      description="This is a Plone Product that makes your user dashboard behave similarly to the iGoogle dashboard.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone dashboard igoogle',
      author='JC Brand',
      author_email='jc@opkode.com',
      url='http://plone.org/products/collective.idashboard',
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
