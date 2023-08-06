from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='twodeg.nosedjango',
      version=version,
      description="A nose plugin for testing django apps",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Framework :: Django",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ben Ford',
      author_email='ben.fordnz@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['twodeg'],
      package_data={'twodeg': ['docs/*.txt']},
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'nose >= 0.10',
      ],
      entry_points="""
      [nose.plugins]
      django = twodeg.nosedjango.nosedjango:NoseDjango
      [zc.buildout]
      default = twodeg.nosedjango.recipe:Recipe
      """,
      )
