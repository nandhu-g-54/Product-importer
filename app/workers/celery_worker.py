from app.celery_app import celery
from app.services.csv_importer import import_csv_service

@celery.task
def import_csv_task(file_path: str):
    return import_csv_service(file_path)
from app.celery_app import celery_app

# Auto-discovers "tasks.import_csv"
celery_app.autodiscover_tasks(['app.services'])
