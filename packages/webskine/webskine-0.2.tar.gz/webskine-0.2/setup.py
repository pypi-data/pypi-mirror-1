from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='webskine',
      version=version,
      description="A simple WSGI blog.",
      long_description="""\
Webskine is a simple and fun weblog. It uses AJAX calls -- actually, asynchronous JSON requests -- to create, edit and delete posts in place. Most of the functionality comes from Paste, Cheetah and jsonstore (on the server side) and jquery and TinyMCE (on the client side).""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi blog',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://dealmeida.net/projects/webskine',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'Paste',
          'PasteScript',
          'PasteDeploy',
          'jsonstore>=0.3',
          'python-dateutil',
          'Cheetah',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = webskine.wsgiapp:make_app

      [paste.paster_create_template]
      webskine = webskine.template:WebskineTemplate
      """,
      )
      
