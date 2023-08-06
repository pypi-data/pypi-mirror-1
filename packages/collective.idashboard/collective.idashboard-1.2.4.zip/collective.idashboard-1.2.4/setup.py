from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('collective', 'idashboard', 'version.txt')[:-1]

long_description = (
                        open("README.txt").read() + "\n" +
                        open(os.path.join("docs", "HISTORY.txt")).read() + "\n" 
    )

setup(name='collective.idashboard',
      version=version,
      description="This Plone add-on product gives your dashboard features similiar to those of the iGoogle dashboard.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone dashboard idashboard igoogle',
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
          'collective.js.jquery',
          'collective.js.jqueryui',
          'collective.alerts'
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
