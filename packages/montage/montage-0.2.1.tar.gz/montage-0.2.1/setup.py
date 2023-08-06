from cropresize import crop_resize
from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='montage',
      version=version,
      description="photogallery using decoupage",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='photo gallery decoupage',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/montage',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        'decoupage',
        'cropresize'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [decoupage.formatters]
      images = montage.formatters:Images
      """,
      )
