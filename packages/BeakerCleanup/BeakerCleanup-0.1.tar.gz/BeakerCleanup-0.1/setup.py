from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='BeakerCleanup',
      version=version,
      description="A beaker plugin that implements a function to be called from the command line via PasteCall.",
      long_description=open('README.txt').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='beaker session database cleanup sqlalchemy delete old',
      author='Linas Juskevicius',
      author_email='linas@idiles.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'tests']),
      include_package_data=True,
      namespace_packages=['beaker', 'beaker.scripts'],
      zip_safe=False,
      tests_require=['Nose>=0.11'],
      test_suite='nose.collector',
      install_requires=[
        'Beaker',
        'SQLAlchemy>=0.5.2',
        'PasteCall',
      ],
      entry_points="""
      """,
      )
