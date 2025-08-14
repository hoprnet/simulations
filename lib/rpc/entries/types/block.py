from typing import Any


class Block:
    def __init__(self, block: Any):
        if isinstance(block, str):
            base: int = 16 if block.startswith("0x") else 10
            self.idx = int(block, base)
        if isinstance(block, int):
            self.idx = block
            
    def __str__(self):
        return hex(self.idx)

    def __repr__(self):
        return f"ChainBlock({self.idx})"

    def __le__(self, other: 'Block'):
        return self.idx <= other.idx

    def __lt__(self, other: 'Block'):
        return self.idx < other.idx

    def __add__(self, other: Any):
        if isinstance(other, Block):
            return Block(hex(self.idx + other.idx))
        else:
            return Block(self.idx + other)

    def __eq__(self, other: Any):
        if not isinstance(other, Block):
            raise NotImplementedError
            
        return self.idx == other.idx