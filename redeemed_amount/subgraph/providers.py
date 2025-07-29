from lib.subgraph.providers import GraphQLProvider


class Fundings(GraphQLProvider):
    query_file = "queries/fundings.graphql"
    params = ['$from: String = ""', '$to_in: [String!] = [""]']
