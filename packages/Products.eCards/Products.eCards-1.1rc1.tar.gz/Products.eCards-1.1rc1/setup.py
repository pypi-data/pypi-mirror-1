from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "eCards", "version.txt")).read().strip()

setup(name='Products.eCards',
      version=version,
      description="eCards is a simple product that allows your website visitors to send e-cards to people via email.",
      long_description=open(os.path.join("README.txt")).read() + "\n" +
                       open(os.path.join("Products", "eCards", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "eCards", "CHANGES.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='Plone Archetypes Content',
      author='Andrew Burkhalter',
      author_email='andrewburkhalter@gmail.com',
      url='http://www.plone.org/products/ecards',
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
