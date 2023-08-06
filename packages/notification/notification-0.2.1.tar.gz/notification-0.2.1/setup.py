from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='notification',
      version=version,
      description="email templating and sending library (supports html and text emails) with wsgi support",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Tim Parkin & Matt Goodall',
      author_email='info@timparkin.co.uk',
      url='http://ish.io',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [paste.filter_factory]
      main = notification.wsgiapp:filter_factory
      mako = notification.wsgiapp:filter_factory_mako
      """,
      )
