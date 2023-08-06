from setuptools import setup, find_packages
import sys, os

version = '0.1'

readme = open('README.txt').read()

setup(name='django-staticblocks',
      version=version,
      description="",
      long_description=readme,
      classifiers=['Framework :: Django'],
      keywords='django template static',
      author='Ethan Jucovy, Rob Marianski',
      author_email='ethan.jucovy@gmail.com',
      url='',
      license='GPLv3 or greater',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'django',
          'djangohelpers',
      ],
      entry_points="""
      """,
      )
