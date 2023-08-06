from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="EntityStore",
      version="0.3.6",
      description="EntityStore - REST interface for CRUD on (RDF) Entities.",
      long_description="""\
EntityStore - provides a REST interface for creation, reading, updating and deleting 'Entities'.
These currently are expressed as objects and described using RDF.
The logging and notification APIs are built around the AMQP standard, and can have arbitrary
authenticated listeners/workers plugging in and providing functionality, such as Lucene/SPARQL
indexes. Uses the python application 'supervisor' to start/stop/control default worker processes via it's
XML-RPC api.
""",
      maintainer="Ben O'Steen",
      maintainer_email="bosteen@gmail.com",
      packages=find_packages(),
      install_requires=['amqpqueue', 'pyworker', 'rdfobject>=0.3.1', 'supervisor', 'web.py', 'mako', 'redis', 'solrpy', 'http4store'],
      )

