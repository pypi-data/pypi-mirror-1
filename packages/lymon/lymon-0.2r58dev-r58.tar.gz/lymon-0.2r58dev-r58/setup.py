from setuptools import setup, find_packages
import sys, os

version = '0.2r58'

setup(name='lymon',
      version=version,
      description="Lymon Web Development Toolkit",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Laureano Arcanio',
      author_email='laureano.arcanio@gmail.com',
      url='http://code.google.com/p/lymon/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
