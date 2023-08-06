from setuptools import setup, find_packages
import sys, os

version = '1.4.6'

setup(name='kss.demo',
      version=version,
      description="KSS (Kinetic Style Sheets) demo",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='KSS Project',
      author_email='kss-devel@codespeak.net',
      url='http://kssproject.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['kss'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
          'kss.core==1.4.7',
          'elementtree'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      dependency_links=[
      ],
      )
