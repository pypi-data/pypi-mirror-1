from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='wafoo',
      version=version,
      description="web application framework of object",
      long_description="""\
""",
      classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi web',
      author='Atsushi Odagiri',
      author_email='aodagx@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
