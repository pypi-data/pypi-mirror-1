from setuptools import setup, find_packages
import os

version = '0.2rc1'

setup(name='collective.viewlet.links',
      version=version,
      description="Viewlet displaying user-editable links on portal or folder level",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='viewlet links',
      author='Liz Dahlstrom and Harald Friessnegger',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/products/collective.viewlet.links',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.z3cform',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
