import os
from celery import Celery
from tickets import tasks

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jump_project.settings')

app = Celery("jump_project")
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()
