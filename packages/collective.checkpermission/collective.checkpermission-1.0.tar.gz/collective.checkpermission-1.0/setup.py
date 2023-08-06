from setuptools import setup, find_packages
import os

version = '1.0'

tests_require=['collective.testcaselayer']

setup(name='collective.checkpermission',
      version=version,
      description="Provides a decorator for protect methods of browser views",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone',
      author='Davide Moro',
      author_email='davide.moro@redomino.com',
      url='http://redomino.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require={'tests':tests_require},
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
