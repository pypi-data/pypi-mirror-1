from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.pivottable',
      version=version,
      description="A class to generate Pivot Tables based on Objects, using your attributes and/or methods, that can use Zope Acquisition to get those.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope python pivot table pivottable',
      author='Simples Consultoria - Luciano Pacheco',
      author_email='products@simplesconsultoria.com.br',
      url='http://dev.plone.org/collective/browser/collective.pivottable',
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
