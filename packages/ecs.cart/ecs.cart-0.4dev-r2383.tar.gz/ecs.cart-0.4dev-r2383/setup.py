from setuptools import setup, find_packages
import sys, os

version = '0.4'

setup(name='ecs.cart',
      version=version,
      description="Package from the ecs suite, that provide a cart object for ecommerce projects",
      long_description=open(os.path.join("README.txt")).read() + "\n" +
                       open("CHANGELOG.txt").read() + "\n" +
                       open(os.path.join("docs", "source", "doc", "README.txt")).read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ecs emencia e-commerce commerce shop cart e-shop',
      author='Lafaye Philippe',
      author_email='lafaye@emencia.com',
      url='http://emencia.com',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      namespace_packages = ['ecs'],
      zip_safe=False,
      test_suite = "nose.collector",
      install_requires=[
          # -*- Extra requirements: -*-
          "paste",
      ],
      entry_points="""
      """,
      )
