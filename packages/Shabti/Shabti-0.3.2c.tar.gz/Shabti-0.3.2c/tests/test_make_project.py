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
authxp_projenv = None

try:
    import migrate
    test_migrate = True
except ImportError:
    test_migrate = False
    
def _get_script_name(script):
    if sys.platform == 'win32':
        script += '.exe'
    return script

def paster_create(project_name, template):
    res = testenv.run(_get_script_name('paster'), 'create', '--verbose', '--no-interactive',
                      '--template=%s' % template,
                      project_name)
    package_name = project_name.lower()
    expect_fn = [package_name, 'development.ini', 'setup.cfg', 'README.txt', 'test.ini',
                 'setup.py', '%s.egg-info' % project_name,
                 ]
    for fn in expect_fn:
        fn = os.path.join(project_name, fn)
        assert fn in res.files_created.keys()
        assert fn in res.stdout
    
    setup = res.files_created[os.path.join(project_name,'setup.py')]
    setup.mustcontain('%s:make_app' % package_name)
    setup.mustcontain('main = pylons.util:PylonsInstaller')
    setup.mustcontain("include_package_data=True")
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

    return projenv


def create_shabti_proj():
    global projenv
    projenv = paster_create('ProjectName', 'shabti')

def create_shabti_auth_proj():
    global auth_projenv
    auth_projenv = paster_create('AuthProjectName', 'shabti_auth')

def create_shabti_auth_xp_proj():
    global authxp_projenv
    authxp_projenv = paster_create('AuthXpProjectName', 'shabti_auth_xp')

def make_model():
    res = projenv.run(_get_script_name('paster')+' model news')
    assert os.path.join('projectname','model','news.py') in res.files_created
    assert os.path.join('projectname','tests','unit','test_news.py') in res.files_created
    assert '?' not in res.stdout

def setup_model():
    projenv_files = os.path.join(os.path.dirname(__file__), 'projenv_files') 
    _do_proj_test(projenv, 'ProjectName',
                  {os.path.join(projenv_files, '__init__.py_tmpl') : os.path.join('projectname', 'model', '__init__.py'),
                   os.path.join(projenv_files, 'websetup.py_tmpl') : os.path.join('projectname', 'websetup.py'),
                   os.path.join(projenv_files, 'development.ini_tmpl') : 'development.ini',
                   os.path.join(projenv_files, 'test.ini_tmpl') : 'test.ini',
                   os.path.join(projenv_files, 'news.json_tmpl') : os.path.join('projectname', 'tests', 'fixtures', 'news', 'newsitems.json' ),
                   os.path.join(projenv_files, 'test_news.py_tmpl') : os.path.join('projectname', 'tests', 'unit', 'test_news.py'),
                   os.path.join(projenv_files, 'news.py_tmpl') : os.path.join('projectname', 'model', 'news.py' )})

    res = projenv.run(_get_script_name('paster')+' setup-app development.ini', expect_stderr='expect_error')


def open_shell():
    res = projenv.run(_get_script_name('paster')+' shell development.ini', expect_stderr='expect_error')


def models():
    res = projenv.run(_get_script_name('nosetests'), expect_stderr='expect_error')


def create_sql():
    res = projenv.run(_get_script_name('paster')+' create_sql development.ini', expect_stderr='expect_error')

def drop_sql():
    res = projenv.run(_get_script_name('paster')+' drop_sql development.ini', expect_stderr='expect_error', stdin='yes')

def reset_sql():
    res = projenv.run(_get_script_name('paster')+' reset_sql development.ini', expect_stderr='expect_error', stdin='yes')

def create_runner_script():
    res = projenv.run(_get_script_name('paster')+' runner --create myscript', expect_stderr='expect_error')
    assert os.path.join('projectname','scripts','myscript.py') in res.files_created
    res = projenv.run(_get_script_name('paster')+' runner myscript development.ini', expect_stderr='expect_error')
    assert '?' not in res.stdout

def migrate_script():
    res = projenv.run(_get_script_name('paster')+' migrate development.ini script script.py', expect_stderr='expect_error')
    assert 'script.py' in res.files_created


def migrate_check():
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
    authprojenv_files = os.path.join(os.path.dirname(__file__), 'authprojenv_files')
    _do_proj_test(auth_projenv, 'AuthProjectName',
                  {os.path.join(authprojenv_files, 'auth_controller.py_tmpl') : os.path.join('authprojectname', 'controllers', 'auth.py'),
                   os.path.join(authprojenv_files, 'development.ini_tmpl') : 'development.ini',
                   os.path.join(authprojenv_files, 'test_auth_controller.py_tmpl') : os.path.join('authprojectname', 'tests', 'functional', 'test_auth_controller.py'),
                   os.path.join(authprojenv_files, 'index.mako_tmpl') : os.path.join('authprojectname', 'templates', 'index.mako')})

def authxp_setup():
    authxpprojenv_files = os.path.join(os.path.dirname(__file__), 'authxpprojenv_files')
    _do_proj_test(authxp_projenv, 'AuthXpProjectName',
                  {os.path.join(authxpprojenv_files, 'news_controller.py_tmpl') : os.path.join('authxpprojectname', 'controllers', 'news.py'),
                   os.path.join(authxpprojenv_files, 'development.ini_tmpl') : 'development.ini',
                   os.path.join(authxpprojenv_files, '__init__.py_tmpl') : os.path.join('authxpprojectname', 'model', '__init__.py'),
                   os.path.join(authxpprojenv_files, 'news.py_tmpl') : os.path.join('authxpprojectname', 'model', 'news.py'),
                   os.path.join(authxpprojenv_files, 'test_news_model.py_tmpl') : os.path.join('authxpprojectname', 'tests', 'unit', 'test_news.py'),
                   os.path.join(authxpprojenv_files, 'test_news_controller.py_tmpl') : os.path.join('authxpprojectname', 'tests', 'functional', 'test_news_controller.py')})
   

def _do_proj_test(projenv, project_name, copydict, emptyfiles=None):
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
                      cwd=os.path.join(testenv.cwd, project_name).replace('\\','/'))

 
def test_project():
    yield (create_shabti_proj, )
    yield (create_shabti_auth_proj, )
    yield (create_shabti_auth_xp_proj, )
    yield (make_model,)
    yield (setup_model, )
    yield (open_shell, )
    yield (models, )
    yield (authxp_setup, )
    yield (auth_controllers, )
    yield (auth_models, )
    yield (create_sql, )
    yield (drop_sql, )
    yield (reset_sql, )
    yield (create_runner_script, )
    if test_migrate:
        yield (migrate_script, )
        yield (migrate_check, )
        yield (migrate_commit, )
        yield (migrate_upgrade, )
        yield (migrate_downgrade, )