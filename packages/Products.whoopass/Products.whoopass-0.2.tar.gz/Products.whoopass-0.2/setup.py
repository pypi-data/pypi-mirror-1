from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
README = open('README.txt').read()
CHANGES = open('CHANGES.txt').read()

version = '0.2'

setup(name='Products.whoopass',
      version = version,
      description = "repoze.who-aware authentication plugin for PAS",
      long_description = '\n\n'.join([README, CHANGES]),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords = '',
      author = 'Agendaless Consulting, Inc.',
      author_email='mailto:tseaver@agendaless.com',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      test_suite="Products.whoopass.tests",
      tests_require = [
          #'repoze.who',
          ],
      install_requires=[
          'setuptools',
          'Products.PluggableAuthService',
      ],
      )
