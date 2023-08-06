import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mod2doctest",
    version = "0.0.2",
    author = "Andrew Carter",
    author_email = "andrewjcarter@gmail.com",
    description = "A way to convert any Python module to a doctest ready doc string.",
    license = "MIT",
    keywords = "doctest unit test",
    url = "http://packages.python.org/mod2doctest/",   # project home page, if any
    py_modules=['mod2doctest'],
    packages=['tests'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
