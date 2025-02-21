from lib.subgraph import Entry


class Ticket(Entry):
    def __init__(
        self,
        id: str,
        amount: str,
        source: str,
    ):
        self.id = id
        self.amount = float(amount)
        self.source = source

    @classmethod
    def fromSubgraphResult(cls, ticket: dict):
        return cls(ticket['id'], ticket['amount'], ticket['channel']['source']['id'])

    @classmethod
    def aggregate(cls, tickets: list) -> dict:
        """
        Compute the sum of ticket amounts for each source
        """
        stats = {
            "total": 0,
            "nodes": {}
        }

        for ticket in tickets:
            if ticket.source not in stats["nodes"]:
                stats["nodes"][ticket.source] = 0
            stats["nodes"][ticket.source] += ticket.amount
            stats["total"] += ticket.amount
        
        return stats
