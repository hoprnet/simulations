from lib.subgraph import GraphQLProvider


class SafesProvider(GraphQLProvider):
    query_file: str = "queries/safes_balance.graphql"

class NFTProvider(GraphQLProvider):
    query_file: str = "queries/nft_boosts.graphql"
