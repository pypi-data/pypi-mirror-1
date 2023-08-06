from setuptools import setup, find_packages
import os

version = '1.0.3'

setup(name='Products.SmartColorWidget',
      version=version,
      description="smart color picker widget for Archetypes",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone widget colorpicker',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://plone.org/products/smartcolorwidget',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
