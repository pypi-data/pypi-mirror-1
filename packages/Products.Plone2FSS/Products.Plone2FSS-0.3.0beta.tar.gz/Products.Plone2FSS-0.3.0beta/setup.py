from setuptools import setup, find_packages
import os

version = '0.3.0'

setup(name='Products.Plone2FSS',
      version=version,
      description="Export File and Image fields from Plone content type to a FSS valid format",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='iw fss plone file image migration',
      author='Keul (Luca Fabbri)',
      author_email='luca.fabbri@redturtle.net',
      url='http://svn.plone.org/svn/collective/Products.Plone2FSS',
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
