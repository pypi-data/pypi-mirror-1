import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "django-testmaker",
    version = "0.1",
    packages = find_packages(),
    author = "Eric Holscher",
    author_email = "eric@ericholscher.com",
    description = "A package to help automate creation of testing in Django",
    url = "http://code.google.com/p/django-testmaker/"
)

