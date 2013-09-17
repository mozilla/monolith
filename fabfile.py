from os.path import join as pjoin

from fabric.api import env, execute, lcd, local, task

from fabdeploytools import helpers
import fabdeploytools.envs

import deploysettings as settings


env.key_filename = settings.SSH_KEY
fabdeploytools.envs.loadenv(settings.CLUSTER)

ROOT, MONOLITH = helpers.get_app_dirs(__file__)

VIRTUALENV = pjoin(ROOT, 'venv')
PYTHON = pjoin(VIRTUALENV, 'bin', 'python')


@task
def create_virtualenv():
    helpers.create_venv(VIRTUALENV, settings.PYREPO,
                        pjoin(MONOLITH, 'requirements/prod.txt'))


@task
def deploy():
    helpers.deploy(
        name='monolith',
        env=settings.ENV,
        cluster=settings.CLUSTER,
        domain=settings.DOMAIN,
        root=ROOT,
        deploy_roles=['web'],
        package_dirs=['monolith', 'venv'])

    helpers.restart_uwsgi(getattr(settings, 'UWSGI', ['monolith']))


@task
def pre_update(ref):
    execute(helpers.git_update, MONOLITH, ref)


@task
def update():
    execute(create_virtualenv)
    with lcd(MONOLITH):
        local('%s setup.py develop' % PYTHON)
        local('%s /usr/bin/virtualenv --relocatable %s' % (PYTHON, VIRTUALENV))
