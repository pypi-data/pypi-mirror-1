from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='kupu.mashups',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Matias Bordese',
      author_email='mbordese@gmail.com',
      url='http://svn.plone.org/svn/collective/kupu,mashups',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['kupu'],
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
