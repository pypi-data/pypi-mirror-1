from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name= 'Tesla',
    version='0.2.2',
    author="beachcoder",
    author_email="danjac_35@yahoo.co.uk",
    url="http://code.google.com/p/tesla-pylons-elixir",
    description='Pylons template with Elixir ORM bindings',
    long_description="""
Tesla
-----

Tesla is a web framework built on Pylons/Paste and Elixir/SQLAlchemy. It includes paster commands for database management, migrations,
and a template with AuthKit integration.
""",
    licence='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=["PasteScript>=1.3", "Pylons>=0.9.5", "Elixir>=0.3.0", "migrate>=0.2.2", "AuthKit>=0.3.0pre5"],
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