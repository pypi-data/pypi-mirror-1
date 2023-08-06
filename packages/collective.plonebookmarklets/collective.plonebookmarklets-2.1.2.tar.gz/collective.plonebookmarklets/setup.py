from setuptools import setup, find_packages
import os

version = '2.1.2'

setup(name='collective.plonebookmarklets',
      version=version,
      description="This product installs an 'Add Bookmarklet' document_action to your Plone site",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='tagging bookmarklets social bookmarking',
      author='enPraxis',
      author_email='info@enpraxis.net',
      url='http://plone.org/products/plonebookmarklets',
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
