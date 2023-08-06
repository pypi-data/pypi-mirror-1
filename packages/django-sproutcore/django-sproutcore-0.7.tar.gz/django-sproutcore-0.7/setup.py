import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "django-sproutcore",
    version = "0.7",
    packages = find_packages(),
    author = "Taavi Taijala, Richard Silver, Eric Ocean",
    author_email = "taavi@taijala.com, corn13read@gmail.com, eric.ocean@me.com",
    description = "A package to help automate creation of sproutcore apps for django",
    url = "http://github.com/erichocean/django-sproutcore/tree/master",
    include_package_data = True
)

