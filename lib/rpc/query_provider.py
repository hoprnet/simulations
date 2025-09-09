import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Callable, Optional

import aiohttp

from lib.rpc.entries.log import Log

BLOCK_SIZE: int = 64

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    pass


class RPCQueryProvider:
    method: str = ""
    exp_type: Callable = str

    def __init__(self, url: str):
        self.url = url
        self.pwd = Path(sys.modules[self.__class__.__module__].__file__).parent
        self.query = {
            "jsonrpc": "2.0",
            "method": self.method,
            # "params": [{"to": "", "data": ""}, "latest"],
            "id": 1,
        }

    #### PRIVATE METHODS ####
    def _get_query(self, params: Optional[dict]) -> dict:
        if params is not None and params != {}:
            self.query["params"] = [params]

        return self.query

    async def _execute(self, params: Optional[dict] = None) -> tuple[dict, dict]:
        self._get_query(params)

        while True:
            try:
                async with (
                    aiohttp.ClientSession() as session,
                    session.post(self.url, json=self.query) as response,
                ):  
                    try:
                        return await response.json(), response.status
                    except Exception as err:    
                        logger.error(f"Error parsing response: {str(err)}")

            except TimeoutError as err:
                logger.error(f"Timeout error : {str(err)}")
                await asyncio.sleep(0.2)  # Retry after a short delay
            except Exception as err:
                logger.error(f"Unknown error {str(err)}")
                await asyncio.sleep(0.2)  # Retry after a short delay

    def _convert_result(self, result: dict, status: int) -> Any:
        if status != 200:
            raise ProviderError(
                f"Error fetching data: {result.get('error', 'Unknown error')}")

        if "result" not in result:
            raise ProviderError(
                "Invalid response format: 'result' key not found")

        if not isinstance(result["result"], self.exp_type):
            raise ProviderError(
                f"Invalid response format: 'result' should be {self.exp_type.__name__}")

        return self.convert_result(result["result"])

    #### PUBLIC METHODS ####
    def convert_result(self, result: Any) -> Any:
        return result

    async def get(self, timeout: int = 30, **kwargs: Any) -> Any:
        try:
            res = await asyncio.wait_for(self._execute(kwargs), timeout)
        except asyncio.TimeoutError:
            logger.error(f"Request to {self.url} timed out after {timeout} seconds")
            return self._convert_result({}, 504)  # HTTP 504 Gateway Timeout
        else:
            return self._convert_result(*res)

    @classmethod
    def get_query(cls, **kwargs: Any) -> dict:
        return cls("")._get_query(kwargs)

class ETHCallRPCProvider(RPCQueryProvider):
    method: str = "eth_call"
    exp_type: Callable = str

class ETHGetLogsRPCProvider(RPCQueryProvider):
    method: str = "eth_getLogs"
    exp_type: Callable = list

    def convert_result(self, result: list[dict]) -> list[Log]:
        return [Log(item) for item in result]

class Web3ClientVersionRPCProvider(RPCQueryProvider):
    method: str = "web3_clientVersion"
    exp_type: Callable = str