class Index:
    def __init__(self, value: str):
        self.value = int(value, 16)

    def __repr__(self):
        return f"Index({self.value})"