from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.jqueryflot',
      version=version,
      description="Flot JQuery implementation for Plone",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone jquery flot plot graph',
      author='Rok Garbas',
      author_email='rok@garbas.si',
      url='http://svn.plone.org/svn/collective/collective.jqueryflot',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'':'src'},
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
