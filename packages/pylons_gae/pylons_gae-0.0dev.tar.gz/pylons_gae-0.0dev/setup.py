from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='pylons_gae',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Amine CHOUKI',
      author_email='surfeurX@gmail.com',
      url='http://www.ledeveloppeur.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "paste"
      ],
      entry_points="""
      [paste.paster_create_template]
      gae = pylons_gae.templates:Create
      """,
      )
