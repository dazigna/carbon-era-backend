
import uuid
from django.db import models
from django.db.models.deletion import SET_NULL
from tree_queries.models import TreeNode

class Unit(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, null=True)
    numerator = models.CharField(max_length=64, null=True)
    denominator = models.CharField(max_length=64, null=True)
    quantity = models.CharField(max_length=64, null=True)
    attribute = models.JSONField(null=True)

    def __str__(self) -> str:
        return f'{self.name}, {self.attribute}, {self.quantity}'


class Category(TreeNode):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.TextField(null=True)

    def __str__(self) -> str:
        return f'{self.pk} - {self.name}, parent: {self.parent}'

class Item(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
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

class Contributor(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.TextField(null=True)

    def __str__(self) -> str:
        return self.name_fr