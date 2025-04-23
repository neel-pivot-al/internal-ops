from django.db import models
from simple_history.models import HistoricalRecords


class BaseHistoryModel(models.Model):
    """
    Mixin for all models that need to track history.
    """

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
