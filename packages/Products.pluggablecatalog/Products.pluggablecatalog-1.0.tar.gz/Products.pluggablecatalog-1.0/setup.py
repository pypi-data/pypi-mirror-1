from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='Products.pluggablecatalog',
      version=version,
      description="pluggablecatalog is a replacement (or rather: a wrapper) for Plone's portal catalog",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Daniel Nouri',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      download_url='http://plone.org/products/pluggablecatalog',
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      """,
      )
