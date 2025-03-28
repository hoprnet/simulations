from lib.subgraph import Entry


class TicketSubStatistics:
    def __init__(self, count: int = 0, value: float = 0):
        self.ticket_count = count
        self.redeemed_value = value

    def increase_count(self, increment: int = 1):
        self.ticket_count += increment

    def increase_value(self, value: float = 0):
        self.redeemed_value += value


class TicketStatistics:
    
    def __init__(self):
        self.nodes: dict[str, TicketSubStatistics] = {}

    @property
    def resume(self):
        value = sum([node.redeemed_value for node in self.nodes.values()])
        count = sum([node.ticket_count for node in self.nodes.values()])
        return TicketSubStatistics(count, value)

    @property
    def as_dict(self):
        return {
            "redeemed_value": self.resume.redeemed_value,
            "ticket_count": self.resume.ticket_count,
            "ticket_issuers": {source: vars(stat) for source, stat in self.nodes.items()}
        }

    def increase_count(self, source: str, increment: int = 1):
        if source not in self.nodes:
            self.nodes[source] = TicketSubStatistics()
        self.nodes[source].increase_count(increment)

    def increase_value(self, source: str, value: float = 0):
        if source not in self.nodes:
            self.nodes[source] = TicketSubStatistics()
        self.nodes[source].increase_value(value)


class Ticket(Entry):
    def __init__(
        self,
        id: str,
        value: str,
        source: str,
    ):
        self.id = id
        self.value = float(value)
        self.source = source

    @classmethod
    def fromSubgraphResult(cls, ticket: dict):
        return cls(ticket['id'], ticket['amount'], ticket['channel']['source']['id'])

    @classmethod
    def aggregate(cls, tickets: list) -> TicketStatistics:
        stats = TicketStatistics()

        for ticket in tickets:
            stats.increase_count(ticket.source)
            stats.increase_value(ticket.source, ticket.value)

        return stats
