from setuptools import setup, find_packages
import sys, os

version = '0.1dev'

setup(name='PrettyTimedelta',
      version=version,
      description="Turn timedeltas into pretty format.",
      keywords='timedelta pretty format date',
      author='Jakub Warmuz',
      author_email='jakub.warmuz@gmail.com',
      packages=find_packages(),
      )
