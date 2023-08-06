import os
from setuptools import setup, find_packages

setup(name='vanguardistas.buildoutsvn',
      version='1.0.0',
      packages=find_packages(),
      namespace_packages=["vanguardistas"],
      install_requires=[
          'zc.buildout'],
      include_package_data = True,
      entry_points = {'zc.buildout.extension': ['default = vanguardistas.buildoutsvn:install']},
      zip_safe = False,
      )
