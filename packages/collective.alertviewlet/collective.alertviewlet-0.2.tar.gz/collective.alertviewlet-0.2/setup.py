from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.alertviewlet',
      version=version,
      description="Allows site administrator to quickly put a global alert on the site",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Antonio Tirabasso; Francesco Merlo',
      author_email='antonio.tirabasso@reflab.it; francesco.merlo@reflab.it',
      url='http://svn.plone.org/collective/collective.alertviewlet',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
