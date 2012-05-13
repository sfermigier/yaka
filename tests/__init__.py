# Hack around the fact that twill (a requirement for Flask-Testing) embeds
# an older version of subprocess.

import os

print os.environ['PATH']
os.environ['PATH'] = "/usr/local/bin:" + os.environ['PATH']

import subprocess