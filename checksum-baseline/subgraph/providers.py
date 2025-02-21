from lib.subgraph import GraphQLProvider


class EventsProvider(GraphQLProvider):
    query_file = "queries/events.graphql"
    params = ["$block_number: String"]

class LastBlockProvider(GraphQLProvider):
    query_file = "queries/last_block.graphql"
    default_key  = ["_meta", "block", "number"]