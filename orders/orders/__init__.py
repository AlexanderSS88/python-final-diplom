from .celery import celery_app

__all__ = ('celery_app',)

default_app_config = 'orders.apps.BackendConfig'