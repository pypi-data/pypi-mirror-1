from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='ecs.cart',
      version=version,
      description="Package from the ecs suite, that provide a cart object for ecommerce projects",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ecs emencia e-commerce commerce shop cart e-shop',
      author='Lafaye Philippe',
      author_email='lafaye@emencia.com',
      url='http://emencia.com',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      namespace_packages = ['ecs'],
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
