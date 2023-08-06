from setuptools import setup, find_packages
import os

version = '1.0'

readme = open(os.path.join('Products', 'Plone3Cleaners', 'README.txt')).read()
history = open(os.path.join('Products', 'Plone3Cleaners', 'HISTORY.txt')).read()
long_description = readme + "\n" + history

setup(name='Products.Plone3Cleaners',
      version=version,
      description="",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Zest Software',
      author_email='m.van.rees@zestsoftware.nl',
      url="",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      """,
      )
