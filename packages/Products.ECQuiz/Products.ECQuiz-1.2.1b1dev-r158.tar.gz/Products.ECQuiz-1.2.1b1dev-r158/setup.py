from setuptools import setup, find_packages
import os

version = '1.2.1b1'

setup(name='Products.ECQuiz',
      version=version,
      description="Quiz module of eduComponents",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='qti',
      author='Otto-von-Guericke-Universit\xc3\xa4t Magdeburg',
      author_email='educomponents@uni-magdeburg.de',
      url='http://plone.org/products/ecquiz',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.DataGridField',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
