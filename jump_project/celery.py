from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jump_project.settings")

app = Celery("jump_project")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# Namespace 'CELERY' means all celery-related config keys
# should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from installed apps
app.autodiscover_tasks()

if os.getenv('DJANGO_SETTINGS_MODULE'):
    from tickets.tasks import remove_expired_cartitems

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
