from setuptools import setup
import os

try:
    reqs = open(os.path.join(os.path.dirname(__file__),'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''

setup(name='django-radio-portal',
      version="2.0",
      description='Application for aggregating shows, their episodes and streams',
      long_description="",
      author='Robert Weidlich',
      author_email='portal@robertweidlich.de',
      url='http://git.xenim.de/streaming/portal/',
      packages=['radioportal'],
      include_package_data=True,
      classifiers=[
          'Framework :: Django',
          ],
      )
