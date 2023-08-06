import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Zope2',
]

version_file = os.path.join('Products', 'PloneGazette', 'version.txt')
version = open(version_file).read().strip()

readme_file= os.path.join('Products', 'PloneGazette', 'README.txt')
desc = open(readme_file).read().strip()
changes_file = os.path.join('Products', 'PloneGazette', 'HISTORY.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nCHANGES\n=======\n\n' +  changes 

setup(name='Products.PloneGazette',
      version=version,
      author='Pilot Systems',
      author_email='',
      maintainer='Radim Novotny',
      maintainer_email='novotny.radim@gmail.com',
      classifiers=CLASSIFIERS,
      keywords='Zope',
      url='http://plone.org/products/plonegazette',
      description='A complete Newsletter product for Plone.',
      long_description=long_description,
      packages=['Products', 'Products.PloneGazette'],
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools'],
      namespace_packages=['Products'],

      )
