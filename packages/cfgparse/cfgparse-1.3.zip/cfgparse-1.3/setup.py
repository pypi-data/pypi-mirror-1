#from setuptools import setupfrom distutils.core import setup
import os

try:
    os.remove('MANIFEST')
except OSError:
    pass

setup(name='cfgparse',
      version='1.3',
      description="Configuration Parser Module",
      author="Daniel M. Gass",
      author_email="dan.gass@gmail.com",
      url="https://sourceforge.net/projects/cfgparse/",
      py_modules=['cfgparse'],
     )
