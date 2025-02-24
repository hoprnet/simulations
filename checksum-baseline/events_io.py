import pickle
from pathlib import Path

from lib.helper import progress_bar

from .subgraph.providers import EventsProvider, LastBlockProvider


class EventsIO:
    def __init__(self, folder: Path):
        self.folder = folder

    def from_local_files(self):
        data = []
        files = list(self.folder.glob("*.pkl"))
        print(
            f"Loading data from {len(files)} files in folder `{self.folder}`")
        for file in files:
            print(f"\rLoading {file.name}", end="")
            with open(file, "rb") as f:
                data.extend(pickle.load(f))
        print("\r" + " " * 100, end="")
        print("\rLoading done!")
        return data

    async def from_subgraph(self, url: str, minblock: int):
        results = await LastBlockProvider(url).get()
        last_block = results[0]

        if minblock >= last_block:
            print("No missing data to load from onchain")
            return []
        else:
            print(f"Loading data from block {minblock} to {last_block}")

        provider = EventsProvider(url)
        data, temp_data = [], []
        idx = 0
        while idx == 0 or len(temp_data) == 6000:
            block_number = int(data[-1]["block_number"]
                               ) if len(data) > 0 else minblock
            
            temp_data = await provider.get(block_number=str(block_number))

            with open(self.folder.joinpath(f"part_{idx}.pkl"), "wb") as f:
                pickle.dump(temp_data, f)
            
            data.extend(temp_data)

            progress_bar(
                block_number,
                last_block,
                (block_number - minblock) / (last_block - minblock),
            )

            idx += 1

        progress_bar(last_block, last_block, 1)
        print("")

        return data
