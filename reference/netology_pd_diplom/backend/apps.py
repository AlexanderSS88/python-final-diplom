from django import AppConfig


class BackendConfig(AppConfig):
    name = 'backend'

    def ready(self):
        """
        импортируем сигналы
        """
