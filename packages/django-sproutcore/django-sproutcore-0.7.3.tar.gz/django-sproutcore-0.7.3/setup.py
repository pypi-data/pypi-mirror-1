import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "django-sproutcore",
    version = "0.7.3",
    packages = ['djangocore', 'polls', 'sproutcore'],
    author = "Taavi Taijala, Richard Silver, Erich Ocean",
    author_email = "taavi@taijala.com, corn13read@gmail.com, eric.ocean@me.com",
    description = "A package to help automate creation of sproutcore apps for django",
    url = "http://github.com/erichocean/django-sproutcore/tree/master",
    license = 'BSD',
    include_package_data = True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)

