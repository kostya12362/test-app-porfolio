from django.db import models


class DBModel(models.Model):
    """Base abstract model using in app."""

    objects = models.Manager()

    @classmethod
    def get_fields(cls) -> list[str]:
        return [i.name for i in cls._meta.get_fields()]

    class Meta:
        abstract = True
