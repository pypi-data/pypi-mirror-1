from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='collective.pfg.sslfield',
      version=version,
      description="New field for PloneFormGen to extract SSL data from the request",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone forms ssl formgeneration',
      author='Mikel Larreategi',
      author_email='mlarreategi@codesyntax.com',
      url='http://svn.plone.org/svn/collective/collective.pfg.sslfield',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.pfg'],
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
