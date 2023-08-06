from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "django_bshell",
    version = "1.0.1",
    description = "Django management command to run bshell, and import all models",
    url = "http://bitbucket.org/schinckel/django-bpython/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = find_packages(exclude='tests'),
    setup_requires = [
    ],
)
