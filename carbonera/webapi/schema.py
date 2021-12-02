from graphene_django import DjangoObjectType
import graphene
from webapi.models import Units 

class UnitsType(DjangoObjectType):
    class Meta:
        model = Units

class Query(graphene.ObjectType):
    all_units = graphene.List(UnitsType)

    def resolve_all_units(self, info):
        return Units.objects.all()

schema = graphene.Schema(query=Query)