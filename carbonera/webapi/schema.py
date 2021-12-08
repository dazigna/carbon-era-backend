from graphene_django import DjangoObjectType
import graphene
from webapi.models import Unit 

class UnitsType(DjangoObjectType):
    class Meta:
        model = Unit

class Query(graphene.ObjectType):
    all_units = graphene.List(UnitsType)

    def resolve_all_units(self, info):
        return Unit.objects.all()

schema = graphene.Schema(query=Query)