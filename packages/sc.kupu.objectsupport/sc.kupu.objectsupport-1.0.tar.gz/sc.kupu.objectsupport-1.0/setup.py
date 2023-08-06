from setuptools import setup, find_packages
import os

version = open(os.path.join("sc", "kupu", "objectsupport", "version.txt")).read().strip()

setup(name='sc.kupu.objectsupport',
      version=version,
      description="",
      long_description=open(os.path.join("sc", "kupu", "objectsupport", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sc', 'sc.kupu'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.kupu >= 1.4.1'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
