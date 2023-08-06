from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='experimental.aggressiveopaquespeedup',
      version=version,
      description="A more aggressive opaquespeedup package to improve performance",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='JeanMichel FRANCOIS aka toutpt',
      author_email='makina-corpus.com',
      url='http://svn.plone.org/svn/collective/experimental.aggressiveopaquespeedup',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['experimental'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.monkeypatcher'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
