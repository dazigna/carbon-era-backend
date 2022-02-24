import django_filters
import graphene
from django.contrib.postgres.search import SearchQuery, SearchVector
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from webapi.models import Category, Item, Unit, Contributor


class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"
        filter_fields = {
            'name': ['iexact'],
            'uuid': ['exact'],
            'parent__name': ['exact', 'isnull'],
        }
        interfaces = (graphene.relay.Node, )

# Filtering
class ItemFilter(django_filters.FilterSet):
    items_by_category_name = django_filters.CharFilter(field_name="category__name", method='filter_items_by_category_name')
    search = django_filters.CharFilter(field_name="name_fr", method="search_fulltext")

    class Meta:
        model = Item
        fields = {
            'name_fr': ['iexact', 'icontains', 'istartswith'],
            'category_str': ['exact', 'icontains', 'istartswith'],
            'category__name':['exact'],
            'uuid': ['exact'],
        }

    def filter_items_by_category_name(self, queryset, name, value):
        cat = Category.objects.get(name=value)
        catDescendants = cat.descendants()
        if catDescendants:
            return queryset.filter(category__name__in=[x.name for x in catDescendants])
        else:
            return queryset.filter(category=cat)

    def search_fulltext(self, queryset, name, value):
        return queryset.annotate(search=SearchVector(name)).filter(search=SearchQuery(value))

class ItemNode(DjangoObjectType):
    class Meta:
        model = Item
        filterset_class = ItemFilter
        interfaces = (graphene.relay.Node, )


class UnitNode(DjangoObjectType):
    class Meta:
        model = Unit
        fields = "__all__"
        filter_fields = ['name', 'quantity', 'uuid']
        interfaces = (graphene.relay.Node, )

class ContributorNode(DjangoObjectType):
    class Meta:
        model = Contributor
        fields = "__all__"
        filter_fields = ['name', 'uuid']
        interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    category = graphene.relay.Node.Field(CategoryNode)
    categories = DjangoFilterConnectionField(CategoryNode)

    item = graphene.relay.Node.Field(ItemNode)
    items = DjangoFilterConnectionField(ItemNode)

    unit = graphene.relay.Node.Field(UnitNode)
    units = DjangoFilterConnectionField(UnitNode)

    contributor = graphene.relay.Node.Field(ContributorNode)
    contributors = DjangoFilterConnectionField(ContributorNode)

schema = graphene.Schema(query=Query)