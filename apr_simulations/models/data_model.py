class DataModel:
    def __init__(self, use_snapshot: bool):
        self.use_snapshot = use_snapshot

    async def get_data(self, folder: str = None):
        if self.use_snapshot:
            if folder is None:
                raise ValueError("folder must be provided when using snapshot")
            self.load_snapshot(folder)
        else:
            await self.get_dynamic_data()
            self.dump_snapshot(folder)

    async def get_dynamic_data(self):
        raise NotImplementedError
    
    def load_snapshot(self, folder: str):
        raise NotImplementedError
    
    def dump_snapshot(self, folder: str):
        raise NotImplementedError
    
    def plot_static(self):
        raise NotImplementedError
    
    def plot_interactive(self):
        raise NotImplementedError