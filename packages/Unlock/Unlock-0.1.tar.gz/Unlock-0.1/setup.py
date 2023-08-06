import setuptools
from setuptools import setup, find_packages

setup(name="Unlock",
      version="0.1",
      description="Client for the Unlock web services",
      long_description="Client code to make calls to the RESTful API at http://unlock.edina.ac.uk for gazetteer, place search and geographic reference text extraction",
      packages=find_packages(),
      #package_data={'': '*.html'},
      install_requires=[],
      author='Jo Walsh',
      author_email='jo.walsh@ed.ac.uk',
      url='http://unlock.edina.ac.uk/code.html',
)	
