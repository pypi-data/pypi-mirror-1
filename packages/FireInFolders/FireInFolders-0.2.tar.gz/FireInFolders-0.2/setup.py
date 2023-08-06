from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='FireInFolders',
      version=version,
      description="Command line utility which excecutes commands in multiple folders",
      long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='util cli',
      author='niteoweb',
      author_email='info@niteoweb.com',
      url='http://www.niteoweb.com/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points={
          'console_scripts': [
              "fire_in_folders = fire_in_folders:main"
          ]
      }
      )
