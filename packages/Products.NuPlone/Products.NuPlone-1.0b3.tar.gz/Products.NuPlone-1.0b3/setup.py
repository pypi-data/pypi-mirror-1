from setuptools import setup, find_packages
import os

version = '1.0b3'

setup(name='Products.NuPlone',
      version=version,
      description="A new theme for Plone 3.0",
      long_description=open("README.txt").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: User Interfaces",
        ],
      keywords='Plone theme tableless',
      author='Cornelis Kolbach and Alexander Limi',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.theme',
          'Plone',
      ],
      )
