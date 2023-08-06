from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='collective.collage.easyslider',
      version=version,
      description="Collage view for content slide.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read()  + "\n" +
                       open(os.path.join("docs", "AUTHORS.txt")).read()  + "\n" +
                       open(os.path.join("docs", "LICENSE.txt")).read()  + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Rcom',
      author_email='info@rcom.com.ar',
      url='http://plone.org/products/collective.collage.easyslider',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.collage'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.Collage',
          'collective.easyslider',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
