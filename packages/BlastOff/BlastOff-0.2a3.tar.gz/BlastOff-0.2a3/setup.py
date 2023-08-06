from setuptools import setup, find_packages
import sys, os

version = '0.2a3'

# OS X: prevent 'tar' from including resource forks ("._*" files)
os.environ['COPYFILE_DISABLE'] = 'true'

setup(
    name='BlastOff',
    version=version,
    description="A Pylons application template providing a working site skeleton configured with SQLAlchemy, mako, repoze.who, ToscaWidgets, TurboMail, WebFlash and (optionally) SchemaBot. The generated app is pre-configured with authentication, login and registration forms, and (optionally) email confirmation.",
    long_description="""\
BlastOff helps accelerate Pylons application development by generating a project with a number of pre-configured dependencies.

Installation
------------

Use pip::

  $ pip install BlastOff


or use setuptools::

  $ easy_install BlastOff


or old school, download the package from http://pypi.python.org/pypi/BlastOff, unpack it and run (as root if required)::

  $ python setup.py install



Usage
-----

Create a new Pylons project from the BlastOff template with::

  $ paster create -t blastoff AppName


You will be prompted for a few options::

  Enter sqlalchemy_url (The SQLAlchemy URL of the database) ['sqlite:///%(here)s/development.db']: 

Specify the database URL that will be used by SQLAlchemy. Defaults to an SQLite database.  For PostgreSQL use something like:: 

  postgres://user:pass@hostname/dbname

::

  Enter use_schemabot (Enable database schema version control using SchemaBot) [True]: 

If True then SchemaBot will be used to automatically mange the SQLAlchemy database schema.

::

  Enter email_confirmation (True/False: New users must click activation link from confirmation email) [True]: 

If True the application will be configured to send a confirmation email to the user upon registration.  The email will contain a link for activating the account before it can be used.  If False no activation confirmation will be configured so users will be able to login immediately after registering.

::

  Enter default_user (Default username to create, password will match username (leave blank for no default user)) ['']:

To have a default user created when the database is set up enter the username here.

After creation the Pylons app is ready to be used.  Before starting the app the database needs to be set up (i.e. tables created).  This is done by using the standard Pylons command::

  $ paster setup-app development.ini

A BlastOff generated project uses SchemaBot to manage database schema changes.  The initial tables will be created by SchemaBot, the default user inserted if that option was selected, and the database marked as schema version 1.  See model/__init__.py within the application source for more information.

To run the application use the standard Pylons command::

  $ paster serve --reload development.ini


Point your browser at the URL http://127.0.0.1:5000/

""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='pylons, template, sqlalchemy, toscawidgets, mako, repoze.who, TurboMail, WebFlash, SchemaBot',
    author='Chris Miles',
    author_email='miles.chris@gmail.com',
    url='http://bitbucket.org/chrismiles/blastoff/',
    download_url='http://pypi.python.org/pypi/BlastOff',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "PasteScript>=1.7.3",
    ],
    entry_points="""
# -*- Entry points: -*-
[paste.paster_create_template]
blastoff=blastoff:BlastOffPackage
""",
)
