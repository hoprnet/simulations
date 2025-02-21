from lib.subgraph import ProviderError

from .entries import Node, Ticket
from .providers import SafesProvider, TicketsProvider


async def safe_to_nodes(safe_address: str) -> list[Node]:
    safe_provider = SafesProvider("SUBGRAPH_SAFES_URL")

    try:
        entries = [Node.fromSubgraphResult(n) for n in (await safe_provider.get(safe=safe_address))]
    except ProviderError as err:
        print(f"get safes: {err}")
        return []
    else:
        return entries


async def nodes_to_tickets(relayers: list[Node]) -> list[Ticket]:
    ticket_provider = TicketsProvider("SUBGRAPH_TICKETS_URL")

    node_addresses = [r.id for r in relayers]

    try:
        entries: list[Ticket] = [Ticket.fromSubgraphResult(t) for t in await ticket_provider.get(source_in=node_addresses)]
    except ProviderError as err:
        print(f"get tickets: {err}")
        return []
    else:
        return entries
