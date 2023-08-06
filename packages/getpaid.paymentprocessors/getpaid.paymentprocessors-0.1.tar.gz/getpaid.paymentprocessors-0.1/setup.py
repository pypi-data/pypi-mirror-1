from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='getpaid.paymentprocessors',
      version=version,
      description="Support multiple payment processors on GetPaid site",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Getpaid Community',
      author_email='getpaid-dev@googlegroups.com',
      url='http://www.plonegetpaid.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['getpaid'],
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
