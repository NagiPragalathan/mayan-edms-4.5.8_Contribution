import json

from django.db import models


class SourceManager(models.Manager):
    def create_backend(self, label, backend_path, backend_data=None):
        self.create(
            backend_path=backend_path, backend_data=json.dumps(
                obj=backend_data or {}
            ), label=label
        )
