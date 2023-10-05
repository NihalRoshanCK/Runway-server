import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab



# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Runway_backend.settings')


app = Celery('Runway_backend')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.beat_schedule= {
#     'send-mail-every-day':{
#         'task':'vehicleapp.tasks.fetch_and_store_news',
#         'schedule': crontab(hour=14,minute=45),

#     }
# }

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')