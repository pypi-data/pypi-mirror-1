from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='slc.mindmap',
      version=version,
      description='Adds export, viewing and editing support for mindmaps in Plone, with an embedded editor from mindmeister.com',
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='mindmeister mindmap syslab slc',
      author='JC Brand, Syslab.com GmbH',
      author_email='brand@syslab.com',
      url='http://plone.org/products/slc.mindmap',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'p4a.subtyper',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
