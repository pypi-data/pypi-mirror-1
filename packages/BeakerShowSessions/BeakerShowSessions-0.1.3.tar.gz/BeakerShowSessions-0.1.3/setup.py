from setuptools import setup, find_packages
import sys, os

version = '0.1.3'

setup(name='BeakerShowSessions',
      version=version,
      description="A Beaker extension to show the active sessions",
      long_description=open('README.txt').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='beaker session database active',
      author='Linas Juskevicius',
      author_email='linas@idiles.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'tests', 'tests.testapp']),
      include_package_data=True,
      namespace_packages=['beaker', 'beaker.scripts'],
      zip_safe=False,
      tests_require=['Nose>=0.11', 'PasteCall'],
      test_suite='nose.collector',
      install_requires=[
          'Beaker',
          'PasteDeploy',
          'SQLAlchemy'
      ],
      entry_points="""
      """,
      )
