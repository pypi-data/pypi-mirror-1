from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="HTTP4Store",
      version="0.1alphadev",
      description="HTTP4Store - python client for 4Store.org (4s-httpd)",
      long_description="""\
This is a python client for the 4Store httpd service - allowing for easy handling of sparql results, and adding, appending and deleting graphs.
""",
      author="Ben O'Steen",
      author_email="bosteen@gmail.com",
      packages=find_packages(exclude='tests'),
      install_requires=['rdflib>=2.4.2', 'simplejson', 'httplib2'],
      )

