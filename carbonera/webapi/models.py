from django.db import models


class Units(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    numerator = models.CharField(max_length=64, blank=True, null=True)
    denominator = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

