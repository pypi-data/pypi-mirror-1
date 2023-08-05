"""
Additional commands for database management:
Commands are:

    model create_sql drop_sql
"""

import sys
import os
import pylons

import migrate.versioning.api as migrate_api

from paste.script.command import Command, BadCommand
from paste.script.filemaker import FileOp
from paste.util import import_string
from paste import deploy

from migrate.versioning.exceptions import KnownError, \
    DatabaseAlreadyControlledError


class SqlCommand(Command):
        
    min_args = 1
    max_args = 2
    group_name = 'tesla'

    default_verbosity = 3

    parser = Command.standard_parser(simulate=True)
    parser.add_option('--dburi',
                      dest='dburi',
                      help="Database URI string")

    def command(self):

        try:

            config_file = os.path.abspath(self.args[0])

            file_op = FileOp(source_dir=os.path.join(os.path.dirname(__file__)))
            base_package = file_op.find_dir('models', True)[0]
            package = __import__(base_package + '.model')
            model = package.model

            app = deploy.loadapp('config:' + config_file)
            context = model.get_context()
            metadata = context.metadata

            try:
                table_name = self.args[1]
                table = metadata.tables[table_name]
            except:
                table = None

            self.sql_command(metadata, table)
            
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)


class CreateSqlCommand(SqlCommand):
    """Create all model tables, or a single table

    The create_sql command will create all tables defined in the elixir metadata, 
    or if a table name is passed it will create that table only. 

    Example usage::
       yourproj% paster create_sql development.ini
       yourproj% paster create_sql development.ini users

    This command will ignore any existing tables. Use the corresponding drop_sql 
    command to delete tables.
    """

    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__

    def sql_command(self, metadata, table):
        if table is None:
            metadata.create_all()
        else:
            table.create()

class DropSqlCommand(SqlCommand):
    """Drop all model tables, or a single table

    The drop_sql command will drop all tables defined in the elixir metadata, 
    or if a table name is passed it will create that table only. 

    Example usage::
       yourproj% paster drop_sql development.ini
       yourproj% paster drop_sql development.ini users

    Use the corresponding create_sql command to create tables.
    """

    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__

    def sql_command(self, metadata, table):
        if raw_input("Are you sure you want to drop these tables, and lose all your data ? ").lower() == 'yes':
            if table is None:
                metadata.drop_all()
            else:
                table.drop()


class ModelCommand(Command):
    """Create a Model and accompanying unit test
    

    The model command will create stub files for a module for Elixir model classes
    and corresponding unit test module.
   
    Example usage::
    
        yourproj% paster model user
        Creating yourproj/yourproj/model/user.py
        Creating yourproj/yourproj/tests/unit/test_user.py
    
    If you'd like to have models underneath a directory, just include
    the path as the model name and the necessary directories will be
    created for you::
    
        yourproj% paster model user/permissions
        Creating yourproj/model/user
        Creating yourproj/yourproj/model/user/permissions.py
        Creating yourproj/yourproj/tests/functional/test_user_permissions.py
    """
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 1
    max_args = 1
    group_name = 'tesla'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--no-test',
                      action='store_true',
                      dest='no_test',
                      help="Don't create the test; just the model")

    def command(self):
        """Main command to create model"""
        try:
            file_op = FileOp(source_dir=os.path.join(os.path.dirname(__file__)))
            try:
                name, directory = file_op.parse_path_name_args(self.args[0])
            except:
                raise BadCommand('No egg_info directory was found')
            
            # Check the name isn't the same as the package
            base_package = file_op.find_dir('model', True)[0]
            if base_package.lower() == name.lower():
                raise BadCommand(
                    'Your model name should not be the same as '
                    'the package name %r.'% base_package
            )
            # Validate the name
            name = name.replace('-', '_')
            validate_name(name)
                        
            # Setup the model
            fullname = os.path.join(directory, name)
            model_name = pylons.util.class_name_from_module_name(
                name.split('/')[-1])
            if not fullname.startswith(os.sep):
                fullname = os.sep + fullname
            testname = fullname.replace(os.sep, '_')[1:]
            test_model_name = 'Test' + name[0].upper() + name[1:]
            file_op.template_vars.update({'name': model_name,
                                          'fname': os.path.join(directory, name),
                                          'package':base_package,
                                          'test_model_name':test_model_name})
            file_op.copy_file(template='model.py_tmpl',
                         dest=os.path.join('model', directory), 
                         filename=name)
            if not self.options.no_test:
                file_op.copy_file(template='test_model.py_tmpl',
                             dest=os.path.join('tests', 'unit'),
                             filename='test_'+testname)
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)


class RunnerCommand(Command):
    """Create and run background scripts
    
    To create a new script, type:
    paster runner --create myscript

    This creates a script, myscript.py, in a scripts/ directory. 

    To run the script, type:
    paster runner myscript development.ini

    This will call the run() function in the script. 

    """

    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 1
    max_args = 2
    group_name = 'tesla'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--create',
                      action='store_true',
                      dest='create',
                      help="Create a new runner script")

    def command(self):
        try:
            file_op = FileOp(source_dir=os.path.join(os.path.dirname(__file__)))
            try:
                name, directory = file_op.parse_path_name_args(self.args[0])
            except:
                raise BadCommand('No egg_info directory was found')
        
            # Check the name isn't the same as the package
            base_package = file_op.find_dir('scripts', True)[0]
            if base_package.lower() == name.lower():
                raise BadCommand(
                    'Your script name should not be the same as '
                    'the package name %r.'% base_package)
            # Validate the name
            name = name.replace('-', '_')
            validate_name(name)
                    
            # Create the script
            fullname = os.path.join(directory, name)
            if self.options.create:
                if not fullname.startswith(os.sep):
                    fullname = os.sep + fullname
                file_op.template_vars.update({'package':base_package})
                file_op.copy_file(template='script.py_tmpl',
                                  dest=os.path.join('scripts', directory), 
                                  filename=name)
            else:
                 try:
                     config_file = os.path.abspath(self.args[1])
                 except IndexError:
                     raise BadCommand('Config filename must be provided')

                 script_name = base_package + '.scripts.' + fullname.replace(os.path.sep, '.')                 
                 mod = import_string.try_import_module(script_name)
                 if mod is None : 
                     raise BadCommand('Script %(name)s does not exist. Run paster runner --create %(name)s to create script', 
                         dict(name = name))
                 mod.run(config_file)
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)
       
              

class MigrateCommand(Command):
    """Runs migration commands

    Handles migrate operations. Usage:
    paster migrate config.ini command [--dburi=uri] [--version=version] [--repository=repository] command_options...

    The following migrate commands are supported:

    script script_path - creates migration script
    test script_path - tests migration script (upgrade and downgrade)    
    commit script_path - commits migration script to repository
    source [dest] - prints migration script of version to file or stdout
    version - repository version
    db_version  - database version
    upgrade [--preview_sql] [--preview_py] - upgrades db to next version
    downgrade [--preview_sql] [--preview_py] - downgrades db to previous version
    """
    
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 2
    group_name = 'tesla'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--dburi',
                      dest='dburi',
                      help="Database URI string")

    parser.add_option('--repository',
                      dest='repository',
                      help="Repository directory")

    parser.add_option('--version',
                      dest='version',
                      help="Database version")

    parser.add_option('--version_table',
                      dest='version_table',
                      help="Database version table")

    parser.add_option('--preview_py',
                      action='store_true',
                      dest='preview_py',
                      help="Preview Python script before running")

    parser.add_option('--preview_sql',
                      action='store_true',
                      dest='preview_sql',
                      help="Preview SQL before running")

    def command(self):

        config_file = os.path.abspath(self.args[0])

        try:
            cmd = getattr(self, '_%s_command' % self.args[1])
        except AttributeError:
            raise BadCommand("%s is not a valid migrate command" % self.args[1])

        file_op = FileOp(source_dir=os.path.join(os.path.dirname(__file__)))
        app = deploy.loadapp('config:' + config_file)
        
        # create repository
        package_name = file_op.find_dir('.')[0]
        repository = self.options.repository or os.path.join(package_name, 'repository')
        try:
            migrate_api.create(repository, package_name, table = self.options.version_table)
        except KnownError:
            pass # repository already created

        # add database to version control
        version = self.options.version
        dburi = self.options.dburi or pylons.config.get('sqlalchemy.default.uri')
        try:
            migrate_api.version_control(dburi, repository)
        except DatabaseAlreadyControlledError:
            pass # database already under control
        
        # run command using pattern _<cmd>_command
        remaining_args = self.args[2:]
        result = cmd(dburi, repository, version, *remaining_args)
        if result: print result

    def _script_command(self, dburi, repository, version, script_path):
        return migrate_api.script(script_path)

    def _commit_command(self, dburi, repository, version, script_path, database=None, operation = None):
        return migrate_api.commit(script_path, repository, database=database, operation=operation, version = version)

    def _test_command(self, dburi, repository, version, script_path):
        return migrate_api.test(script_path, repository, dburi)

    def _version_command(self, dburi, repository, version):
        return migrate_api.version(repository)

    def _db_version_command(self, dburi, repository, version):
        return migrate_api.db_version(dburi, repository)

    def _source_command(self, dburi, repository, version, dest=None):
        return migrate_api.source(version, dest, repository)

    def _upgrade_command(self, dburi, repository, version):
        return migrate_api.upgrade(dburi, repository, version, 
                            preview_sql = self.options.preview_sql, 
                            preview_py = self.options.preview_py)

    def _downgrade_command(self, dburi, repository, version):
        return migrate_api.downgrade(dburi, repository, version, 
                            preview_sql = self.options.preview_sql, 
                            preview_py = self.options.preview_py)

    def _drop_version_control_command(self, dburi, repository, version):
        return migrate_api.drop_version_control(dburi, repository)

def validate_name(name):
    """Validate that the name for the model isn't present on the
    path already"""
    if not name:
        # This happens when the name is an existing directory
        raise BadCommand('Please give the name of a model.')
