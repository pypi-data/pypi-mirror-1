import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

from xml.dom import minidom

metadata_file = os.path.join(os.path.dirname(__file__),
                             'collective', 'phantasy',
                             'profiles', 'default', 'metadata.xml')
metadata = minidom.parse(metadata_file)
version = metadata.getElementsByTagName("version")[0].childNodes[0].nodeValue
version = str(version).strip()

setup(name='collective.phantasy',
      version=version,
      description="dynamic theme for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                       open(os.path.join("docs", "TODO.TXT")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='theme skin dynamic-skin',
      author='Jean-mat Grimaldi & Gilles Lenfant\'s good advice and moral support',
      author_email='jeanmat.grimaldi@gmail.com',
      url='http://plone.org/products/collective-phantasy',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender>=1.5',
          'Products.SmartColorWidget>=1.1.1',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
