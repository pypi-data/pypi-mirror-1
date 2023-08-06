from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='Products.OneTimeTokenPAS',
      version=version,
      description="PAS Plugin, login using a token that can be only used once.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone"
        ],
      keywords='Plone PAS plugin token',
      author='Kim Chee Leong',
      author_email='leong@gw20e.com',
      url='http://www.gw20e.com/',
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
