from setuptools import setup, find_packages
import os

version = '1.2.1'

setup(name='se.portlet.gallery',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Miroslaw Ochodek',
      author_email='Miroslaw.Ochodek@gmail.com',
      url='http://plone.org/products/gallery-portlet',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['se', 'se.portlet'],
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
