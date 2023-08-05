from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
import setuptools
setup(
    name = "DAG",
    version = "0",
    packages = find_packages(),
    description='An implementation of a directed acyclic graph.',
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='BSD',
    platforms=['Any'],
    url="http://entitycrisis.blogspot.com/",
    long_description="""
dag.py is a tiny implementation of a directed acyclic graph structure, commonly used for... stuff, 
including scenegraphs.
""" 
)

