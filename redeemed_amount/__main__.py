import asyncio
import random
from typing import Any

from api_lib.headers.authorization import Bearer
from dotenv import load_dotenv

from lib.helper import envvar
from lib.hoprd_api.balance import Balance
from lib.hoprd_api.hoprd_api import HoprdAPI
from lib.hoprd_api.response_objects import OwnChannel
from lib.subgraph.providers import GraphQLProvider

from .subgraph.providers import Fundings

load_dotenv()

async def main():
    # Fetching the total amount in CT channels
    host_format: str = envvar("HOST_FORMAT")
    token: str = envvar("TOKEN")
    deployment: str = envvar("DEPLOYMENT")
    environment: str = envvar("ENVIRONMENT", default="prod")

    apis: list[HoprdAPI] = [
        HoprdAPI(host_format % (deployment, idx, environment), Bearer(token), "/api/v4") for idx in range(1, 6)
    ]

    channels: list[OwnChannel] = sum([(await api.channels(False)).outgoing for api in apis], [])

    total_channel_stake = sum([channel.balance for channel in channels], Balance.zero("wxHOPR"))
    print(f"{'Total channel stake':30s}: {round(total_channel_stake, 2).as_str}")

    # Fetching the total amount in CT safe
    safe_stake = (await random.choice(apis).balances()).safe_hopr
    print(f"{'Total safe stake':30s}: {round(safe_stake, 2).as_str}")
    
    # Fetching the total funds sent to CT safe
    fundings_vars: dict[str, Any] = {
        "to_in": ["0x4afa6a5265ae7ba332e886be3bce5b16c861dd9f"],
        "from": "0xd9a00176cf49dfb9ca3ef61805a2850f45cb1d05",
    }
    funding_provider: GraphQLProvider = Fundings("SUBGRAPH_FUNDINGS_URL")
    ct_funds: float = sum([Balance(f"{r['amount']} wxHOPR") for r in await funding_provider.get(**fundings_vars)], Balance.zero("wxHOPR")) + envvar("FUNDS_CONSTANT", type=Balance)

    print(f"{'Total funds amount':30s}: {round(ct_funds, 2).as_str}")

    redeemed_amount = ct_funds - safe_stake - total_channel_stake
    print(f"{'Redeemed amount':30s}: {round(redeemed_amount, 2).as_str}")

if __name__ == "__main__":
    asyncio.run(main())
