from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "pygnet",
    version = "0.1",
    packages = find_packages(),
    description='pygnet is a minimal layer on top of Twisted, for pygame.',
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='MIT',
    platforms=['Any'],
    url="http://code.google.com/p/pygnet/",
    long_description="""pygnet allows a client and server to send each other marshalled 
objects. It integrates well with pygame.
""" 
)


