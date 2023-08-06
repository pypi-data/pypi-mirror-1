from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='Products.ReflectoImageScales',
      version=version,
      description="Thumbnails for Reflecto images",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone',
      author='Laurence Rowe',
      author_email='laurence@lrowe.co.uk',
      url='http://pypi.python.org/pypi/Products.ReflectoImageScales',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
