from setuptools import setup, find_packages
import os

version = '1.1rc1'

setup(name='Products.TinyMCE',
      version=version,
      description="Adds support for TinyMCE, a platform independent web based Javascript HTML WYSIWYG editor, to Plone.",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n\n" +
                       open("CHANGES.txt").read() + "\n\n" +
                       open(os.path.join("docs", "CONTRIBUTERS.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='editor editors tinymce wysiwyg',
      author='Four Digits',
      author_email='rob@fourdigits.nl',
      url='http://plone.org/products/tinymce',
      license='LGPL',
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
