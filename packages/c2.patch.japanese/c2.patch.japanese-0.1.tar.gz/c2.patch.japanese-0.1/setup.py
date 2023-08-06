from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='c2.patch.japanese',
      version=version,
      description="Patches for Japanese on Plone 3.x,",
      long_description="""This is useful patches for Japanese package.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone patch Japanese',
      author='Manabu Terada',
      author_email='terada@cmscom.jp',
      url='http://www.cmscom.jp',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'c2.patch.plone3mail',
          'Products.BigramSplitter',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
