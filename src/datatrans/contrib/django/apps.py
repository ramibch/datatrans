from django.apps import AppConfig


class DjDatatransConfig(AppConfig):
    name = "datatrans.contrib.djdatatrans"
    verbose_name = "Datatrans Integration"

    def ready(self):
        pass
