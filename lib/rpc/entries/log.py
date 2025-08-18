from dataclasses import fields

from api_lib.objects.response import APIfield, APIobject, JsonResponse

from .types.block import Block
from .types.index import Index


@APIobject
class Log(JsonResponse):
    address: str
    block_hash: str = APIfield("blockHash")
    block_number: Block = APIfield("blockNumber")
    data: str
    log_index: Index = APIfield("logIndex")
    removed: bool
    topics: list[str]
    transaction_hash: str = APIfield("transactionHash")
    transaction_index: Index = APIfield("transactionIndex")

    @property
    def as_dict(self) -> dict:
        return {key: str(getattr(self, key)) for key in [f.name for f in fields(self)]}
