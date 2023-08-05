from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "FibraNet",
    version = "8",
    packages = find_packages(),
    py_modules=['nanothreads','gherkin','nanotubes'],
    description='A cooperative threading and event driven framework with simple network capabilities.',
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='BSD',
    platforms=['Any'],
    url="http://cheeseshop.python.org/pypi/FibraNet",
    long_description="""
The FibraNet package provides an event dispatch mechanism, a cooperative scheduler, an asynchronous networking library
and a safe, fast serializer for simple Python types. It is designed to simplify applications which need to simulate concurrency, 
particularly games.
""" 
)


