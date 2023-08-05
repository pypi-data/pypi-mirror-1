from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = '0.2.5'

setup(
    name= 'Tesla',
    version=version,
    author="beachcoder",
    author_email="danjac_35@yahoo.co.uk",
    keywords='web wsgi framework sqlalchemy elixir pylons paste template',
    description='Pylons template with Elixir ORM bindings',
    long_description="""
Tesla
======

Tesla is a web framework built on Pylons/Paste and Elixir/SQLAlchemy. It includes paster commands for database management, migrations, 
and model scaffolding, plus AuthKit integration. With just a little bit of glue Tesla gives you the best Python web development libraries around today.

Current Status
---------------

Tesla %s described on this page is stable.

There is also an unstable `development version
<http://tesla-pylons-elixir.googlecode.com/svn/trunk/#egg=Tesla-dev>`_ of Tesla.

Download and Installation
-------------------------

Tesla can be installed with `Easy Install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

    > easy_install Tesla

More information
----------------

Check out the project home page on `Google Code <http://code.google.com/p/tesla-pylons-elixir/>`_.

""" % version,
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=["PasteScript>=1.3", "Pylons==dev,>=0.9.6dev-r2134", "SAContext>=0.3.0",
                      "Elixir>=0.3.0", "migrate>=0.2.2", "AuthKit>=0.3.0pre5"],
    include_package_data=True,
    entry_points="""
        [paste.paster_command]
        runner=tesla.commands:RunnerCommand
        migrate=tesla.commands:MigrateCommand
        model=tesla.commands:ModelCommand
        create_sql=tesla.commands:CreateSqlCommand
        drop_sql=tesla.commands:DropSqlCommand
        [paste.paster_create_template]
        tesla=tesla.template:TeslaTemplate
        tesla_auth=tesla.template:TeslaAuthTemplate
    """)