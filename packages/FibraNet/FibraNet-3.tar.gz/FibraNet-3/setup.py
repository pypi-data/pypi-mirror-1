from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "FibraNet",
    version = "3",
    packages = find_packages(),
    py_modules=['nanothreads','gherkin'],
    description='A cooperative threading and event driven framework.',
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='BSD',
    platforms=['Any'],
    long_description="""
FibraNet includes a global event dispatcher, and a concurrency 
simulator (using Python generator functions) / cooperative threading 
system with pause/resume, kill/end functions, and some facilities
to handle CPU blocking operations. 

It is the successor to the EventNet package and the
nanothreads module.
""" 
)


