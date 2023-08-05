Introduction to Tesla
---------------------

This document is relevant to Tesla version 0.2.6.

Tesla is a Python MVC-based web framework designed to make building web apps easy and fast. It's really just a thin layer of glue around some best-of-breed Python libraries, namely:

- Pylons (web framework) (http://www.pylonshq.com)
- SQLAlchemy (ORM and SQL generation) (http://www.sqlalchemy.org)
- Elixir (declarative layer for SQLAlchemy) (LINK)
- Paste (WSGI server and other tools) (http://pythonpaste.org)
- FormEncode (form validation) (http://formencode.org)

In addition to these core libraries Tesla makes optional use of the migrate library for handling database migrations with SQLAlchemy. 

It is strongly suggested that you at least familiarize yourself with the documentation of these core libraries first.

Tesla is named after the great 20th century scientist Nikola Tesla (http://www.wikipedia.org/nikola_tesla).

Philosophy and design goals
___________________________

The main goal of Tesla was to create a fast and easy way to build web applications in Python. Of the existing web frameworks, Pylons seemed the best fit because of its good design, support for the WSGI standard, and re-use of pre-existing components and good ideas from other certain other frameworks, such as routes and helpers. However Pylons was deliberately by design ORM-agnostic, and developers who otherwise were attracted to Pylons were turned off by the hoops they had to jump through to get SQLAlchemy or another ORM working with Pylons. 

Around the same time, SQLAlchemy was emerging as the most well-considered Python ORM. SQLAlchemy, although flexible as an SQL query library, was not so easy to get working with as an ORM compared with for example Rails' ActiveRecord or Django's ORM. The Elixir library proved an excellent solution to this as a declarative layer over SQLAlchemy. 

Tesla started as a simple template with glue code for Pylons and SQLAlchemy/Elixir so that developers could get started quickly with these libraries. Some additional paster command line tools were added for common handlng database management tasks, inspired by similar tools in Rails and Django. 

The AuthKit library was also widely used by Pylons developers for handling authentication/authorization work. An additional Tesla template, tesla_auth, was written integrating AuthKit, as well as providing very basic classes for User, Group and Permission entities. However, the author decided to remove the AuthKit dependency due to various design and documentation issues with that library.

Getting started
_______________

Tesla can be installed from the Cheeseshop (LINK) using `setuptools`. Alternatively you can download the latest version from Cheeseshop (LINK) or Tesla's Google Code project page (http://tesla-pylons-elixir.googlecode.com/downloads). You can also install the latest development version of Tesla from SVN at https://tesla-pylons-elixir.googlecode.com/svn. However, this is the "cutting edge" version and is not always guaranteed to work.

If you are installing using setuptools, just type:

> easy_install -U Tesla

If installing from source, change to the source directory and type

> python setup.py install

If using the development version from SVN:

> python setup.py develop

Setuptools will try to locate and install all the relevant libraries with the correct versions for you. There may be some issues with this, for example if a site is unavailable at the time, so it may be required to manually download and install some libraries. Hopefully, this won't happen and you shouldn't need to do anything more to install Tesla.

Creating an application
_______________________

As with Pylons, you create a new skeleton application by typing the following:

> paster create -t <template_name> <project-name>

If you type `paster create --list-templates` you will see a list of available application templates. The Tesla templates are:

* tesla - default Tesla project template 
* tesla_auth - creates additional code for handling authentication 
* tesla_auth_xp - same as tesla_auth, with row-level permissions

The last template, tesla_auth_xp, is experimental. This will be merged with tesla_auth at some point in the future (probably in version 0.2.7). The tesla_auth template features are explained in further detail below.

Paster commands
_______________

Tesla uses the `paster` command line tool that comes with Paste. Most of the common paster commands are explained in the Pylons documentation. Tesla adds some extra commands of its own, mainly for database management:

> paster model <model_name> [--no-test]

Creates a skeleton Python module, `<model_name>.py`, in the `model` directory of your Tesla application. In addition, a corresponding skeleton unit test module, `test<model_name>.py`,  is added to the `tests/unit` directory of your Tesla package, along with a directory for storing your test fixtures and other fixtures. If the `--no-test` flag is passed then the test files are not created.

> paster create_sql [--table=table] [--setup] config-file

Creates all tables (i.e. CREATE TABLE) based on available model classes. The `config-file` argument is always required, e.g. development.ini. You must provide the correct URI to your database in the configuration setting `sqlalchemy.default.uri` (see (LINK) for the correct URI for your database vendor). 

Note that for a class to be "visible" to the database commands, you have to import the class in the `__init__.py` file of your `model` package, for example:

from mymodel import MyModel

You can optionally pass in the name of a single table to create_sql with the --table argument. The --setup flag will run `setup-app`, i.e. the `websetup.py` file of your application, once the tables have been created.

> paster drop_sql [--table=table] config-file

Drops all available tables (i.e. DROP TABLE), or a single named table if given in the --table argument.

> paster reset_sql [--table=table] [--setup] config-file

Drops all available classes and then re-creates them (or single table given in --table argument). As with create_sql, you can pass the --setup flag to run `websetup.py`.

> paster runner --create <script_name>

Creates a skeleton Python script, `<script_name>.py`, in the `scripts` directory of your Tesla application package. This script is used for running background tasks outside your web application, for example with cron.

> paster runner <script-name> config-file

Runs the script created with `runner --create`. This line can be used for example with cron for running repetitive or timed tasks. The config-file argument (e.g. development.ini) is compulsory.

Migrations
__________

Tesla uses the `migrate` library (LINK), a Google Summer of Code project for running database migrations with SQLAlchemy. Note that the migrate library is not being actively maintained at the moment, and the eventual intention is to re-write the migrate library to work in a more simple manner with Tesla. 

Tesla integrates a number of migration tasks with paster. See the migrate documentation and source code for an explanation of these commands; they are just summarized here.

> paster migrate config-file migration-command 
    [--dburi=uri] [--repository=repo_dir] [--version=version] 
    [--version_table=version_table] [--preview_py] [--preview_sql]

The config-file argument is the name of your configuration file (e.g. development.ini). The argument migration_command may be one of the following:

* commit
* test
* version
* db_version
* source
* upgrade
* downgrade
* drop_version_control

Template engine
_______________

Tesla uses Mako (http://www.makotemplate.org) by default, which is the default template engine used by Pylons (the default engine used to be Myghty). Mako is very fast and flexible. However, if you want to use another template engine, such as Genshi (LINK) feel free to do so. Any template engine that is compatible with Buffet can be used. Consult the Pylons documentation on this.

You are also free to use whatever Javascript/AJAX library you like (although some of the Pylons/Webhelpers functions are dependent on Prototype and Scriptaculous). The author personally recommends jQuery (http://www.jquery.com) but YMMV.

Authentication
______________

The `tesla_auth` template comes with boilerplate authentication code to help you get started. This includes:

* controller-level permission-handling
* action-level permission handling (decorators)
* authentication helpers
* basic identity classes (User, Group and Permission)

The idea behind the tesla_auth template is to do the 80% hard/repetitive work for you and get out of your way for the last 20%. For example, the User class only has the bare minimum of fields such as username and password. It's up to you to add additional fields according to your domain requirements, such as address or phone number. In addition, the default password encryption (using SHA1) may not be stringent enough certain security requirements; again you are free to rewrite the template-generated code to suit your needs. 

The template creates a set of permission classes (located in `lib/permissions.py` inside your Tesla application package) which can be used at the controller or action level, or as helpers in your templates. You can easily extend these classes or create your own. In addition there are three Elixir identity classes (User, Group and Permission) which store the relevant authentication and authorization information to the database. They are located in `lib/model/user.py`. The `@authorize` decorator, located in `lib/decorators.py`, can be used in conjunction with the permission classes. See the source code for more information on using this decorator.

Note that tesla_auth previously required the AuthKit library (LINK). as of version 0.2.6 this is no longer the case.
 
The `tesla_auth_xp` template includes code for row-level permissions. This allows you to set permissions on individual instances rather than just system-wide permissions. For example, you could have a NewsItem class with "edit" and "delete" permissions set for each NewsItem instance. The permissions system is implemented as an Elixir Statement, `has_permissions`. The relevant code is located in `model/permissions.py` in your Tesla application package. One feature of this system is that you can override permission checking, for example granting default "edit" permission to the author of a NewsItem. This makes it quite flexible in more complex situations.

In addition the tesla_auth_xp template provides a sub-class of BaseController, ModelController. The ModelController instance will automatically lookup an instance of the given model class if the "id" parameter is passed in the URL, also handling permission checks if needed. 

The tesla_auth_xp template is experimental (i.e. use at your own risk) and will be merged with the tesla_auth and default tesla templates in future versions.

Reporting bugs and asking questions
___________________________________

If you have found any bugs or other issues with Tesla, report them at the Google Code project page(LINK). However, ensure that the issue lies with Tesla and not with one of the libraries it uses, such as SQLAlchemy or Pylons. In that case, it's probably better to report the bug at the relevant discussion group.

If you have any questions or suggestions regarding Tesla, probably the best place to ask is the Pylons Google discussion group (LINK) or Pylons IRC channel (LINK). The author of Tesla often frequents there and may be able to help you.


