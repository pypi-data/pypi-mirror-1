from setuptools import setup, find_packages
import os

# TODO: why isn't this egg packaging the top-level *.txt files?

here = os.path.abspath(os.path.dirname(__file__))
VERSION = open(os.path.join(here, 'VERSION.txt')).readline().strip()
README  = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(
    name        = "koansys.django.authradius",
    author      = "Chris Shenton",
    author_email= "chris@koansys.com",
    description = "Django can authenticate against a RADIUS server",
    version     = VERSION,
    long_description = README + "\n\n" + CHANGES,
    license     = "BSD",
    keywords    = "authentication",
    url         = "http://koansys-django-authradius.googlecode.com/",
    classifiers = [
    "Programming Language :: Python",
    "Development Status :: 5 - Production/Stable",
    "Framework :: Django",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: BSD License",
    ],
    zip_safe    = False,
    packages    = find_packages(),
    package_data        = { "": ["*.txt", "*.rst"],},
    include_package_data = True,
    namespace_packages   = ["koansys", "koansys.django"],
    install_requires=["pyrad >= 1.1"],
)
