from setuptools import setup, find_packages
import os

version = '0.2.1'

setup(name='anthill.tal.macrorenderer',
      version=version,
      description="Rendering ZPT macros from python code made easy",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope zpt macros render python',
      author='Simon Pamies',
      author_email='s.pamies@banality.de',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['anthill', 'anthill.tal'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
