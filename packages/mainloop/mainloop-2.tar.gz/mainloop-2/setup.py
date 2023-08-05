from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension

packages = find_packages()

setup(
    name = "mainloop",
    version = "2",
    url="http://code.google.com/p/corsair-redux/wiki/mainloop",
    packages = packages,
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='MIT',
    platforms=['Any'],
    description="A class which provides a fixed duration simulation loop with frame skipping when needed.",
)

