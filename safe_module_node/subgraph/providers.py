from lib.subgraph.providers import GraphQLProvider


class SafeModulePairs(GraphQLProvider):
    query_file = "queries/safe_module_pairs.graphql"


class ModuleNodePairs(GraphQLProvider):
    query_file = "queries/module_node_pairs.graphql"
