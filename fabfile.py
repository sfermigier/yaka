from fabric.api import env, run, cd, local, put, sudo

env.hosts = ['oss4cloud.org']

STAGING_DIR = "yaka-crm/staging"
PRODUCTION_DIR = "yaka-crm/production"
NATIVE_PACKAGES = "python-pip poppler-utils imagemagick python-dev " \
    "libjpeg-dev libxslt1-dev make libreoffice unoconv"


def vagrant():
  # change from the default user to 'vagrant'
  env.user = 'vagrant'
  # connect to the port-forwarded ssh
  env.hosts = ['127.0.0.1:2222']

  # use vagrant ssh key
  result = local('vagrant ssh-config | grep IdentityFile', capture=True)
  env.key_filename = result.split()[1]


def update():
  """Updates Debian/Ubuntu's package list"""
  sudo('apt-get -y update')

def upgrade():
  """Perform a safe upgrade"""
  update()
  sudo('aptitude -yv safe-upgrade')

def setup():
  # XXX: Is this really needed?
  ENV = "DEBCONF_TERSE=yes DEBIAN_PRIORITY=critical DEBIAN_FRONTEND=noninteractive"
  sudo("export %s" % ENV)

  for pkg in NATIVE_PACKAGES.split(" "):
    sudo("%s apt-get -yu install %s" % (ENV, pkg))
  sudo("pip -q install virtualenv")
  sudo("pip -q install tox")

def push():
  local("make clean")
  local("rm -f /tmp/yaka.tgz")
  local("tar czf /tmp/yaka.tgz --exclude .git --exclude .tox .")
  put("/tmp/yaka.tgz", "/tmp/yaka.tgz")

def stage():
  push()

  run("mkdir -p %s" % STAGING_DIR)
  with cd(STAGING_DIR):
    run("tar zxf /tmp/yaka.tgz")
    run("tox -e py27")

def deploy():
  stage()

  run("mkdir -p %s" % PRODUCTION_DIR)
  with cd(PRODUCTION_DIR):
    run("tar zxf /tmp/yaka.tgz")
    run("virtualenv env")
    run("env/bin/python setup.py develop -U")
