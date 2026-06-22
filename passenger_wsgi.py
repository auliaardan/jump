import os
import sys

PROJECT_ROOT = "/home/jumpcom/django"

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "jump_project.settings",
)

from jump_project.wsgi import application
