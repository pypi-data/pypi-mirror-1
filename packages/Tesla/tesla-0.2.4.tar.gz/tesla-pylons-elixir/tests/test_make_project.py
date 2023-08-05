import urllib
import os
import shutil
from paste.fixture import *
import pkg_resources
for spec in ['PasteScript', 'Paste', 'PasteDeploy', 'pylons']:
    pkg_resources.require(spec)

template_path = os.path.join(
    os.path.dirname(__file__), 'filestotest').replace('\\','/')

test_environ = os.environ.copy()
test_environ['PASTE_TESTING'] = 'true'

testenv = TestFileEnvironment(
    os.path.join(os.path.dirname(__file__), 'output').replace('\\','/'),
    template_path=template_path,
    environ=test_environ)

projenv = None
auth_projenv = None
    
def _get_script_name(script):
    if sys.platform == 'win32':
        script += '.exe'
    return script

def paster_create(project_name, template):
    res = testenv.run(_get_script_name('paster'), 'create', '--verbose', '--no-interactive',
                      '--template=%s' % template,
                      project_name,
                      'version=0.1',
                      )
    package_name = project_name.lower()
    expect_fn = [package_name, 'development.ini', 'setup.cfg', 'README.txt', 'test.ini',
                 'setup.py', '%s.egg-info' % project_name,
                 ]
    for fn in expect_fn:
        fn = os.path.join(project_name, fn)
        assert fn in res.files_created.keys()
        assert fn in res.stdout
    
    setup = res.files_created[os.path.join(project_name,'setup.py')]
    setup.mustcontain('0.1')
    setup.mustcontain('%s:make_app' % package_name)
    setup.mustcontain('main=pylons.util:PylonsInstaller')
    setup.mustcontain("include_package_data=True")
    assert '0.1' in setup
    testenv.run(_get_script_name('python')+' setup.py egg_info',
                cwd=os.path.join(testenv.cwd, project_name).replace('\\','/'),
                expect_stderr=True)
    projenv = TestFileEnvironment(
        os.path.join(testenv.base_path, project_name).replace('\\','/'),
        start_clear=False,
        template_path=template_path,
        environ=test_environ)
    projenv.environ['PYTHONPATH'] = (
        projenv.environ.get('PYTHONPATH', '') + ':'
        + projenv.base_path)

    file(os.path.join(projenv.base_path, 
        'development.ini'), 'a').write('sqlalchemy.default.uri=sqlite:///%s.db\nsqlalchemy.default.echo=True' % package_name)

    file(os.path.join(projenv.base_path, 
        'test.ini'), 'a').write('sqlalchemy.default.uri=sqlite:///test-%s.db\nsqlalchemy.default.echo=True' % package_name)

    return projenv

def create_tesla_proj():
    global projenv
    projenv = paster_create('ProjectName', 'tesla')

def create_tesla_auth_proj():
    global auth_projenv
    auth_projenv = paster_create('AuthProjectName', 'tesla_auth')
    projenv_files = os.path.join(os.path.dirname(__file__), 'authprojenv_files')
    file(os.path.join(auth_projenv.base_path, 
        'development.ini'), 'a').write('''

authkit.enable = true
authkit.method = forward
authkit.cookie.secret = secret_string
authkit.signin = /login/
authkit.cookie.signout = /login/signout/
''')

def make_model():
    res = projenv.run(_get_script_name('paster')+' model sample')
    assert os.path.join('projectname','models','sample.py') in res.files_created
    assert os.path.join('projectname','tests','unit','test_sample.py') in res.files_created
    assert '?' not in res.stdout

def setup_model():
    projenv_files = os.path.join(os.path.dirname(__file__), 'projenv_files') 
    _do_proj_test(projenv, 
                  {os.path.join(projenv_files, '__init__.py_tmpl') : os.path.join('projectname', 'models', '__init__.py'),
                   os.path.join(projenv_files, 'websetup.py_tmpl') : os.path.join('projectname', 'websetup.py'),
                   os.path.join(projenv_files, 'test_news.py_tmpl') : os.path.join('projectname', 'tests', 'unit', 'test_news.py'),
                   os.path.join(projenv_files, 'news.py_tmpl') : os.path.join('projectname', 'models', 'news.py' )})
    res = projenv.run(_get_script_name('paster')+' setup-app development.ini', expect_stderr='expect_error')

def open_shell():
    res = projenv.run(_get_script_name('paster')+' shell development.ini', expect_stderr='expect_error')

def models():
    res = projenv.run(_get_script_name('nosetests'), expect_stderr='expect_error')

def create_sql():
    res = projenv.run(_get_script_name('paster')+' create_sql development.ini', expect_stderr='expect_error')

def drop_sql():
    res = projenv.run(_get_script_name('paster')+' drop_sql development.ini', expect_stderr='expect_error', stdin='yes')

def create_runner_script():
    res = projenv.run(_get_script_name('paster')+' runner --create myscript', expect_stderr='expect_error')
    assert os.path.join('projectname','scripts','myscript.py') in res.files_created
    res = projenv.run(_get_script_name('paster')+' runner myscript development.ini', expect_stderr='expect_error')
    assert '?' not in res.stdout

def migrate_script():
    res = projenv.run(_get_script_name('paster')+' migrate development.ini script script.py', expect_stderr='expect_error')
    assert 'script.py' in res.files_created

def migrate_t_est():
    res = projenv.run(_get_script_name('paster')+' migrate development.ini test script.py', expect_stderr='expect_error')
    assert 'Success' in res.stdout

def migrate_commit():
    res = projenv.run(_get_script_name('paster')+' migrate development.ini commit script.py', expect_stderr='expect_error')
    assert not os.path.exists(os.path.join(projenv.base_path, 'script.py'))

def migrate_upgrade():
    res = projenv.run(_get_script_name('paster')+' migrate development.ini upgrade', expect_stderr='expect_error')
    assert 'done' in res.stdout

def migrate_downgrade():
    res = projenv.run(_get_script_name('paster')+' migrate development.ini downgrade', expect_stderr='expect_error')

def auth_models():
    res = auth_projenv.run(_get_script_name('nosetests'), expect_stderr='expect_error')

def auth_controllers():
    pass

def _do_proj_test(projenv, copydict, emptyfiles=None):
    """Given a dict of files, where the key is a filename in filestotest, the value is
    the destination in the new projects dir. emptyfiles is a list of files that should
    be created and empty."""
    if not emptyfiles:
        emptyfiles = []
    for original, newfile in copydict.iteritems():
        projenv.writefile(newfile, frompath=original)
    for fi in emptyfiles:
        projenv.writefile(fi)
    res = projenv.run(_get_script_name('nosetests')+' -d',
                      expect_stderr=True,
                      cwd=os.path.join(testenv.cwd, 'ProjectName').replace('\\','/'))

 
def test_project():
    yield (create_tesla_proj, )
    yield (create_tesla_auth_proj, )
    yield (make_model,)
    yield (setup_model, )
    yield (open_shell, )
    yield (models, )
    yield (auth_models, )
    yield (create_sql, )
    yield (drop_sql, )
    yield (create_runner_script, )
    yield (migrate_script, )
    yield (migrate_t_est, )
    yield (migrate_commit, )
    yield (migrate_upgrade, )
    yield (migrate_downgrade, )