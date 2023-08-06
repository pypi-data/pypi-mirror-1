import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Zope2',
]

version_file = os.path.join('Products', 'SecureMaildropHost', 'version.txt')
version = open(version_file).read().strip()

readme_file= os.path.join('Products', 'SecureMaildropHost', 'README.txt')
desc = open(readme_file).read().strip()
changes_file = os.path.join('Products', 'SecureMaildropHost', 'CHANGES.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nCHANGES\n=======\n\n' +  changes 

setup(name='Products.SecureMaildropHost',
      version=version,
      author='Jarn',
      author_email='info@jarn.com',
      maintainer='Martijn Pieters',
      maintainer_email='',
      classifiers=CLASSIFIERS,
      keywords='Zope',
      url='http://plone.org/products/securemaildrophost',
      description='SecureMaildropHost marries SecureMailHost and MaildropHost, making this a drop-in replacement for SecureMailHost.',
      long_description=long_description,
      packages=['Products', 'Products.SecureMaildropHost'],
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools'],
      namespace_packages=['Products'],

      )
