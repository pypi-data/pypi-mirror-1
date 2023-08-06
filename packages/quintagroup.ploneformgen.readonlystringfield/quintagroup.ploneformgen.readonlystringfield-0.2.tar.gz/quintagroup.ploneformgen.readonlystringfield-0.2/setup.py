from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='quintagroup.ploneformgen.readonlystringfield',
      version=version,
      description="Readonly String Field for PloneFormGen product",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone form generator readonly field',
      author='Vitaliy Podoba',
      author_email='piv@quintagroup.com',
      url='http://quintagroup.com/services/plone-development/products/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.ploneformgen'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PloneFormGen',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
