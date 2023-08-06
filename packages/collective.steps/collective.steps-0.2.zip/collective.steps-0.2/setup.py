from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.steps',
      version=version,
      description="Steps to manage a plone site with Stepper",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Jean-Michel FRANCOIS aka toutpt',
      author_email='jeanmichel.francois@makina-corpus.com',
      url='http://svn.plone.org/svn/collective/collective.steps',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
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
