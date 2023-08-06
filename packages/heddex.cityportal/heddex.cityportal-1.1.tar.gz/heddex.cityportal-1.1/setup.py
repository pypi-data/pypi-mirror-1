from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='heddex.cityportal',
      version=version,
      description="An installable theme for Plone 3",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme skin heddex theo michael krishtopa',
      author='Michael Krishtopa',
      author_email='michael.krishtopa@gmail.com',
      url='http://www.heddex.biz',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['heddex'],
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
