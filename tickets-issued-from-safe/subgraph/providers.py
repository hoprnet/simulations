import asyncio
from pathlib import Path
from typing import Optional, Union

import aiohttp


class ProviderError(Exception):
    pass


class GraphQLProvider:
    query_file = None
    params = []

    def __init__(self, url: str):
        self.url = url
        self.pwd = Path(__file__).parent.joinpath("queries")
        self._initialize_query(self.query_file, self.params)

    #### PRIVATE METHODS ####
    def _initialize_query(
        self, query_file: str, extra_inputs: Optional[list[str]] = None
    ):
        if extra_inputs is None:
            extra_inputs = []

        self._default_key, self._sku_query = self._load_query(query_file, extra_inputs)

    def _load_query(self, path: Union[str, Path], extra_inputs: list[str] = []) -> str:
        """
        Loads a graphql query from a file.
        :param path: Path to the file. The path must be relative to the ct-app folder.
        :return: The query as a string.
        """
        inputs = ["$first: Int!", "$skip: Int!", *extra_inputs]

        header = "query (" + ",".join(inputs) + ") {"
        footer = "}"
        with open(self.pwd.joinpath(path)) as f:
            body = f.read()

        return body.split("(")[0], ("\n".join([header, body, footer]))

    async def _execute(self, query: str, variable_values: dict) -> tuple[dict, dict]:
        """
        Executes a graphql query.
        :param query: The query to execute.
        :param variable_values: The variables to use in the query (dict)"""

        try:
            async with aiohttp.ClientSession() as session, session.post(
                self.url, json={"query": query, "variables": variable_values}
            ) as response:
                return await response.json(), response.headers
        except TimeoutError as err:
            print(f"Timeout error: {err}")
        except Exception as err:
            print(f"Unknown error: {err}")
        return {}, None

    async def _test_query(self, key: str, **kwargs) -> bool:
        """
        Tests a subgraph query.
        :param key: The key to look for in the response.
        :param kwargs: The variables to use in the query (dict).
        :return: True if the query is successful, False otherwise.
        """
        kwargs.update({"first": 1, "skip": 0})

        try:
            response, _ = await asyncio.wait_for(
                self._execute(self._sku_query, kwargs), timeout=30
            )
        except asyncio.TimeoutError:
            print("Query timeout occurred")
            return False
        except ProviderError as err:
            print(f"ProviderError error: {err}")
            return False

        return key in response.get("data", [])

    async def _get(self, key: str, **kwargs) -> dict:
        """
        Gets the data from a subgraph query.
        :param key: The key to look for in the response.
        :param kwargs: The variables to use in the query (dict).
        :return: The data from the query.
        """
        page_size = 1000
        skip = 0
        data = []

        while True:
            kwargs.update({"first": page_size, "skip": skip})
            try:
                response, headers = await asyncio.wait_for(
                    self._execute(self._sku_query, kwargs), timeout=30
                )
            except asyncio.TimeoutError:
                print("Timeout error while fetching data from subgraph.")
                break
            except ProviderError as err:
                print(f"ProviderError error: {err}")
                break

            if response is None:
                break

            if "errors" in response:
                print(f"Internal error: {response['errors']}")

            try:
                content = response.get("data", dict()).get(key, [])
            except Exception as err:
                print(f"Error while fetching data from subgraph: {err}")
                break
            data.extend(content)

            skip += page_size
            if len(content) < page_size:
                break

        try:
            if headers is not None:
                print(
                    f"Subgraph attestations {headers.getall('graph-attestation')}"
                )
        except UnboundLocalError:
            # raised if the headers variable is not defined
            pass
        except KeyError:
            # raised if using the centralized endpoint
            pass
        return data

    #### DEFAULT PUBLIC METHODS ####
    async def get(self, key: str = None, **kwargs):
        """
        Gets the data from a subgraph query.
        :param key: The key to look for in the response. If None, the default key is used.
        :param kwargs: The variables to use in the query (dict).
        :return: The data from the query.
        """

        if key is None and self._default_key is not None:
            key = self._default_key
        else:
            print(
                "No key provided for the query, and no default key set. Skipping query..."
            )
            return []
        
        return await self._get(key, **kwargs)

    async def test(self, **kwargs):
        """
        Tests a subgraph query using the default key.
        :param kwargs: The variables to use in the query (dict).
        :return: True if the query is successful, False otherwise.
        """
        if self._default_key is None:
            print(
                "No key provided for the query, and no default key set. Skipping test query..."
            )
            return False

        return await self._test_query(self._default_key, **kwargs)


class TicketsProvider(GraphQLProvider):
    query_file = "tickets.graphql"
    params = ['$source_in: [String!] = [""]']


class SafesProvider(GraphQLProvider):
    query_file = "safe_to_nodes.graphql"
    params = ['$safe: String = ""']