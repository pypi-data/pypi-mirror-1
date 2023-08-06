from setuptools import setup, find_packages
import os

version = '1.0beta1'

setup(name='slc.mindmap',
      version=version,
      description='Add editing, viewing and exporting support for mindmaps in Plone via an embedded mindmeister.com editor.',
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='mindmeister mindmap syslab slc',
      author='J-C Brand, Syslab.com GmbH',
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
