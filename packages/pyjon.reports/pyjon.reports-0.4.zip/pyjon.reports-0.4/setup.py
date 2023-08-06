from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='pyjon.reports',
      version=version,
      description="This is a reporting bird.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='pdf template report rml splitting',
      author='Jonathan Schemoul, Jerome Collette',
      author_email='jonathan.schemoul@gmail.com, collette.jerome@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pyjon'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'genshi >= 0.5',
          'z3c.rml >= 0.7'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
