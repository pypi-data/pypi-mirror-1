from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='wsgihatenaauth',
      version=version,
      description="wsgi middlewar",
      long_description="""\
wsgi middle ware to authorization with Hatena Auth API.

usage::
 from wsgiref.simple_server import make_server, demo_app
 from wsgihatenaauth import HatenaAuthHandler

 apiKey = yourHatenaAuthApiKey
 secret = yourHatenaAuthSercretKey

 app = HatenaAuthHandler(apiKey=apiKey, secret=secret)(demo_app)
 httpd = make_server('', 8000, app)
 httpd.serve_forever()

""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi middleware',
      author='Atsushi Odagiri',
      author_email='aodagx@gmail.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        'pycrypto'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
