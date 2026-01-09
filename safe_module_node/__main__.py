import asyncio

import click
from dotenv import load_dotenv

from lib.helper import asynchronous
from safe_module_node.subgraph import ModuleNodePairs, SafeModulePairs

load_dotenv()

class ModuleOwnerSafeTriplet:
    def __init__(self, safe_address: str, module_address: str, owner: str):
        self.safe_address = safe_address
        self.module_address = module_address
        self.owner = owner

    def __hash__(self):
        return hash(f"{self.safe_address} {self.module_address} {self.owner}")

    def __eq__(self, other):
        return hash(self) == hash(other)

@click.command()
@click.option('--network', default='dufour')
@click.option("--output-file", default="output.csv")
@asynchronous
async def main(network: str, output_file: str):
    module_safe_fixes = {
        "rotsee": {
            "0x0fe056adc6af51614f60c12f5416b7cd13bd7b64": "0x0fe056adc6af51614f60c12f5416b7cd13bd7b64",
            "0xf9f30eb37b1440d7b269245a8c2cafbd249bc53e": "0xbe9e2703209838e44c9d88ec5d504e77e6f23033",
            "0x9c3dca847702d2a684304b4d11cc07f7a272eab0": "0xb64d4e728a4a590dbf661726c85b57b787d90f19",
            "0x138ff63e88237afc928c15bc4bc6ed54d4ba649e": "0x7a2a74b26f24f39b35d02773102585203cce2567",
            "0x27baf3c6b90281ed8c37b7122b76426d39228b00": "0xdC0DeA7A62b02Ce24CC8ce8Dead861614D15c3C1"
        },
        "dufour": {}
    }

    module_owner_fixes = {
        "rotsee": {
            "0x0fe056adc6af51614f60c12f5416b7cd13bd7b64": "0x4ff4e61052a4dfb1be72866ab711ae08dd861976",
            "0xf9f30eb37b1440d7b269245a8c2cafbd249bc53e": "0x4ff4e61052a4dfb1be72866ab711ae08dd861976",
            "0x9c3dca847702d2a684304b4d11cc07f7a272eab0": "0x4ff4e61052a4dfb1be72866ab711ae08dd861976",
            "0x138ff63e88237afc928c15bc4bc6ed54d4ba649e": "0x01bfbcb6a2924b083969ce6237adbbf3bfa7de13",
            "0x27baf3c6b90281ed8c37b7122b76426d39228b00": "0x4ff4e61052a4dfb1be72866ab711ae08dd861976"
        },
        "dufour": {}
    }
    
    safe_module_provider = SafeModulePairs(f"SUBGRAPH_HOPR_NODE_{network.upper()}")
    module_node_provider = ModuleNodePairs(f"SUBGRAPH_HOPR_NODE_{network.upper()}")

    subgraph_results = await safe_module_provider.get()

    safe_module_pairs: dict[str, str] = { res["module"]["id"]: res["safe"]["id"] for res in subgraph_results } | module_safe_fixes[network]

    module_owner_pairs: dict[str, str] = {res["module"]["id"]: res["safe"]["owners"]
                                          [0]["owner"]["id"] for res in subgraph_results} | module_owner_fixes[network]

    
    triplets: set[ModuleOwnerSafeTriplet] = set(ModuleOwnerSafeTriplet(safe_module_pairs.get(res["module"]["id"], "UNKWN"), res["module"]["id"], module_owner_pairs.get(res["module"]["id"], "UNKWN")) for res in await module_node_provider.get())

    with open(output_file, "w") as f:
        f.write("address,module_address,chain_key,deployed_block,deployed_tx_index,deployed_log_index\n")

        index = 0
        for triplet in triplets:
            if "UNKWN" in (triplet.safe_address, triplet.module_address, triplet.owner):
                continue
            f.write(f"{triplet.safe_address},{triplet.module_address},{triplet.owner},30000000,{index},0\n")
            index += 1


if __name__ == "__main__":
    asyncio.run(main())