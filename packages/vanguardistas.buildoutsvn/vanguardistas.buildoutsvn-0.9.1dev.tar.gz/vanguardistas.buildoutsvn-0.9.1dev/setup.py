import os
from setuptools import setup, find_packages

setup(name='vanguardistas.buildoutsvn',
      version='0.9.1dev',
      packages=find_packages(),
      namespace_packages=["vanguardistas"],
      install_requires=[
          'zc.buildout'],
      include_package_data = True,
      zip_safe = False,
      )
