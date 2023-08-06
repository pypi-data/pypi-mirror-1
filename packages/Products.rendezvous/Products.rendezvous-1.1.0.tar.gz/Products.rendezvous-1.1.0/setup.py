from setuptools import setup, find_packages
import os

version = '1.1.0'

setup(name='Products.rendezvous',
      version=version,
      description="A timeboard to select a rendez-vous for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: User Interfaces",
        "Framework :: Plone",
        ],
      keywords='',
      author='Vincent Fretin and Michael Launay',
      author_email='development@ecreall.com',
      url='https://svn.ecreall.com/public/Products.rendezvous',
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
