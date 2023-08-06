from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="PyWorker",
      version="0.2.3",
      long_description="A set of classes that help simplify the creation of workers that listen to queues and perform activities",
      description="""PyWorker - Worker classes for performing queued tasks""",
      maintainer="Ben O'Steen",
      maintainer_email="bosteen@gmail.com",
      packages=find_packages(),
      install_requires=['simplejson', 'httplib2'],
      )

