from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='webskine',
      version=version,
      description="A simple WSGI blog.",
      long_description="""\
Webskine is a simple and fun weblog. It uses AJAX calls -- actually, asynchronous JSON requests -- to create, edit and delete posts in place. Most of the functionality comes from Paste, Cheetah and simplejson (on the server side) and jquery and TinyMCE (on the client side).""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi blog',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://dealmeida.net/projects/webskine',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'PasteDeploy',
          'jsonstore',
          'python-dateutil',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = webskine.wsgiapp:make_app
      """,
      )
      
