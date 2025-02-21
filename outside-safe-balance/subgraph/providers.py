from lib.subgraph import GraphQLProvider


class SafesProvider(GraphQLProvider):
    query_file = "queries/safes_balance.graphql"