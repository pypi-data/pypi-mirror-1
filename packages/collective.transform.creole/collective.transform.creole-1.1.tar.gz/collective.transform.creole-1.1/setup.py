from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.transform.creole',
      version=version,
      description="Creole wiki text transform for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Clayton Parker',
      author_email='info AT claytron DOT com',
      url='https://svn.plone.org/svn/collective/collective.transform.creole',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.transform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'creoleparser'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
