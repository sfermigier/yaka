from fabric.api import env, run, cd, local, put, sudo, task
from fabric.context_managers import prefix

APT_PREFIX = "DEBCONF_TERSE=yes DEBIAN_PRIORITY=critical DEBIAN_FRONTEND=noninteractive"


STAGING_DIR = "yaka/staging"
PRODUCTION_DIR = "yaka/production"
NATIVE_PACKAGES = "python-pip poppler-utils imagemagick python-dev " \
    "libjpeg-dev libxslt1-dev make libzmq-dev"

# Deactivated for now
#NATIVE_PACKAGES += " libreoffice unoconv"


@task
def prod():
  env.hosts = ['oss4cloud.org']
  env.user = 'yaka'


@task
def vagrant():
  # change from the default user to 'vagrant'
  env.user = 'vagrant'
  # connect to the port-forwarded ssh
  env.hosts = ['127.0.0.1:2222']

  # use vagrant ssh key
  result = local('vagrant ssh-config | grep IdentityFile', capture=True)
  env.key_filename = result.split()[1]


@task
def upgrade():
  """Perform a safe upgrade"""
  sudo('apt-get -y update')
  sudo('%s aptitude -y safe-upgrade' % APT_PREFIX)


@task
def setup():
  for pkg in NATIVE_PACKAGES.split(" "):
    sudo("%s apt-get -yu install %s" % (APT_PREFIX, pkg))

  sudo("pip -q install virtualenv")
  sudo("pip -q install tox")

  run("mkdir -p %s" % STAGING_DIR)
  run("mkdir -p %s" % PRODUCTION_DIR)
  with cd(PRODUCTION_DIR):
    run("virtualenv env")


@task
def push():
  local("make clean")
  local("rm -f /tmp/yaka.tgz")
  local("tar czf /tmp/yaka.tgz --exclude .git --exclude .tox .")
  put("/tmp/yaka.tgz", "/tmp/yaka.tgz")


@task
def stage():
  with cd(STAGING_DIR):
    run("tar zxf /tmp/yaka.tgz")
    run("tox -e py27")


@task
def deploy():
  with cd(PRODUCTION_DIR):
    run("tar zxf /tmp/yaka.tgz")
    run("env/bin/python setup.py develop")
    run("env/bin/pip install circus")

#    circus_ini = open("circus.ini").read()
#    circus_ini = circus_ini.replace("@@HOME@@", "/users/" + env.user)
#    with open("/tmp/circus.ini", "wc") as fd:
#      fd.write(circus_ini)
#    put("/tmp/circus.ini", "circus.ini")
#
#    run("if [ ! -e circus.pid ] ; then env/bin/circusd --daemon --pidfile circus.pid circus.ini; fi;")
#    run("env/bin/circusctl reload")


@task
def clean():
  with cd(PRODUCTION_DIR):
    run("make clean")


@task(alias="run")
def run_():
  with cd(PRODUCTION_DIR):
    with prefix(". env/bin/activate"):
      run("make run")


@task(default=True)
def default():
  push()
  stage()
  deploy()
  run_()

