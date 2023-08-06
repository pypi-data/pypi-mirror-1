import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyjack",
    version = "0.0.2",
    author = "Andrew Carter",
    author_email = "andrewjcarter@gmail.com",
    description = "A way to hijack python methods and functions and attach callbacks or alter functionality.",
    license = "MIT",
    keywords = "python function method hijack signal slot signals slots observer publisher subscriber",
    url = "http://code.google.com/p/pyjack/",   # project home page, if any
    py_modules=['pyjack'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
