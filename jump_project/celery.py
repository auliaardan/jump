from celery import Celery

app = Celery('jump_project')

# Configure Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Manually import tasks to ensure registration
import tickets.tasks
