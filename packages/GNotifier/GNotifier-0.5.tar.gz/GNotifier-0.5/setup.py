from setuptools import setup, find_packages
import sys, os

version = '0.5'

setup(name='GNotifier',
      version=version,
      description="web service to send notification via gmail/gtalk",
      long_description=open('README.txt').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='google gtalk gmail notification',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://www.gawel.org/docs/GNotifier/index.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'WebOb',
          'PasteScript',
          'simplejson',
          'restkit',
          'gunicorn',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = notifier.server:main
      [console_scripts]
      gnotify = notifier:main
      """,
      )
