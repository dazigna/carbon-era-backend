from graphene_django import DjangoObjectType
import graphene
from webapi.models import Unit, Item, Category 

class ItemsType(DjangoObjectType):
    class Meta:
        model = Item

class CategoriesType(DjangoObjectType):
    class Meta:
        model = Category

class UnitsType(DjangoObjectType):
    class Meta:
        model = Unit

class Query(graphene.ObjectType):
    all_units = graphene.List(UnitsType)
    all_items = graphene.List(ItemsType)
    all_categories = graphene.List(CategoriesType)

    def resolve_all_units(self, info):
        return Unit.objects.all()

    def resolve_all_items(self, info):
        return Item.objects.all()

    def resolve_all_categories(self, info):
        return Category.objects.all()

schema = graphene.Schema(query=Query)