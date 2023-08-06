from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.portlet.map',
      version=version,
      description="Google Map portlet",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Riccardo Lemmi',
      author_email='riccardo@reflab.it',
      url='http://www.reflab.it',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.Maps', # http://pypi.python.org/pypi/Products.Maps/2.0
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
