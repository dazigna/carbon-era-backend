from dataclasses import fields
import django_filters
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from webapi.models import Category, Item, Unit


class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"
        filter_fields = {
            'name': ['exact'],
            'parent__name': ['exact', 'isnull'],
        }
        interfaces = (graphene.relay.Node, )

# Filtering
class ItemFilter(django_filters.FilterSet):
    items_by_category_name = django_filters.CharFilter(field_name="category__name", method='filter_items_by_category_name')

    class Meta:
        model = Item
        # fields = "__all__"
        fields = {
            'name_fr': ['exact', 'icontains', 'istartswith'],
            'category_str': ['exact', 'icontains', 'istartswith'],
            'category__name':['exact']
        }

    def filter_items_by_category_name(self, queryset, name, value):
        cat = Category.objects.get(name=value)
        catDescendants = cat.descendants()
        if catDescendants:
            return Item.objects.filter(category__name__in=[x.name for x in catDescendants])
        else:
            return Item.objects.filter(category=cat)

class ItemNode(DjangoObjectType):
    class Meta:
        model = Item
        filterset_class = ItemFilter
        interfaces = (graphene.relay.Node, )


class UnitNode(DjangoObjectType):
    class Meta:
        model = Unit
        fields = "__all__"
        filter_fields = ['name', 'quantity']
        interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    category = graphene.relay.Node.Field(CategoryNode)
    categories = DjangoFilterConnectionField(CategoryNode)

    item = graphene.relay.Node.Field(ItemNode)
    items = DjangoFilterConnectionField(ItemNode)

    unit = graphene.relay.Node.Field(UnitNode)
    units = DjangoFilterConnectionField(UnitNode)

schema = graphene.Schema(query=Query)