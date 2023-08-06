from setuptools import setup, find_packages
import sys, os

version = '0.4'

setup(name='SaladeDeFruits',
      version=version,
      description="A skinning middleware",
      long_description=open('README.txt').read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Operating System :: OS Independent',
         ],
      keywords='wsgi middleware skin lxml pyquery',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://www.gawel.org/docs/SaladeDeFruits/index.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'WebOb',
          'Paste',
          'WSGIProxy',
          'pyquery',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_app_factory]
      main = saladedefruits.saladier:make_salade
      """,
      )
