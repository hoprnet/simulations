from lib.subgraph import GraphQLProvider


class TicketsProvider(GraphQLProvider):
    query_file = "queries/tickets.graphql"
    params = ['$source_in: [String!] = [""]']


class SafesProvider(GraphQLProvider):
    query_file = "queries/safe_to_nodes.graphql"
    params = ['$safe: String = ""']
