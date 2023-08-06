from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="AMQPQueue",
      version="0.3.2",
      description="AMQPQueue - Python Queue interface for AMQP",
      long_description="""\
AMQPQueue - Python Queue interface for AMQP
""",
      packages=find_packages(),
      install_requires=['amqplib', 'simplejson', 'httplib2'],
      )

