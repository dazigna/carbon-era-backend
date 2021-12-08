import uuid
from django.db import models
from django.db.models.deletion import SET_NULL


class Unit(models.Model):
    name = models.CharField(max_length=64, null=True)
    numerator = models.CharField(max_length=64, null=True)
    denominator = models.CharField(max_length=64, null=True)

    def __str__(self) -> str:
        return f'{self.name}, {self.numerator}'

class Category(models.Model):
    name = models.TextField(null=True)
    parent = models.IntegerField(null=True)

class Item(models.Model):
    name_fr = models.TextField(null=True)
    name_en = models.TextField(null=True)
    attribute_fr = models.TextField(null=True)
    attribute_en = models.TextField(null=True) 
    category_str = models.TextField(null=True)
    tag_fr = models.TextField(null=True)
    tag_en = models.TextField(null=True)
    unit_str = models.TextField(null=True)
    confidence = models.IntegerField(null=True)
    total_poste = models.FloatField(null=True)
    co2f = models.FloatField(null=True)
    ch4f = models.FloatField(null=True)
    ch4b = models.FloatField(null=True)
    n2o = models.FloatField(null=True)
    co2b = models.FloatField(null=True)
    other_ghg = models.FloatField(null=True)

    category = models.ForeignKey(Category, null=True, on_delete=SET_NULL)
    unit = models.ForeignKey(Unit, null=True, on_delete=SET_NULL)
    
    def __str__(self) -> str:
        return self.name_fr

