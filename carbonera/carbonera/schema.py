import graphene
# import webapi.schema
import webapi.schema_relay

class Query(webapi.schema_relay.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)