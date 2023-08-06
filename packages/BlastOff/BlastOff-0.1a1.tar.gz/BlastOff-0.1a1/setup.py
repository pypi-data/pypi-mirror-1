from setuptools import setup, find_packages
import sys, os

version = '0.1a1'

setup(
    name='BlastOff',
    version=version,
    description="A Pylons template providing a working site skeleton configured with SQLAlchemy, mako, repoze.who, SchemaBot, ToscaWidgets, TurboMail and WebFlash.",
    long_description="""\
BlastOff is simply a template and applications created from it will have no dependency on BlastOff after creation. The application will be a standard Pylons project with a number of pre-configured dependencies to help accelerate development of Pylons applications.
""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Chris Miles',
    author_email='miles.chris@gmail.com',
    url='http://bitbucket.org/chrismiles/blastoff/',
    download_url='http://pypi.python.org/pypi/BlastOff',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Paste>=1.7",
    ],
    entry_points="""
# -*- Entry points: -*-
[paste.paster_create_template]
blastoff=blastoff:BlastOffPackage
""",
)
