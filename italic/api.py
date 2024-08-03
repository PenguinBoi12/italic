from re import sub
from os import environ
from dotenv import load_dotenv
from inspect import isawaitable

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError

load_dotenv()


class Result:
    def __init__(self, data):
        self.errors = []

        for name, value in data.items():
            setattr(self, self._format_name(name), self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Result(value) if isinstance(value, dict) else value

    def _format_name(self, name):
        return sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


class CursifClient:
    CURSIF_ENDPOINT = environ.get('CURSIF_ENDPOINT', "https://api.codesociety.xyz/api")

    def __init__(self, token, on_success=None, on_query=None, on_error=None):
        self._client = None
        self.token = token

        # callback
        self.on_success = on_success
        self.on_query = on_query
        self.on_error = on_error

    @property
    def client(self) -> Client:
        if not self._client:
            transport = AIOHTTPTransport(
                url=self.CURSIF_ENDPOINT,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            self._client = Client(
                transport=transport,
                fetch_schema_from_transport=True,
                parse_results=True
            )

        return self._client

    async def query(self, query, variables={}, on_success=None, on_error=None) -> Result:
        self._on_query()

        try:
            result = await self.client.execute_async(
                gql(query),
                variable_values=variables
            )

            self._on_query_success(Result(result), on_success)
        except TransportQueryError as e:
            self._on_query_error(Result({"errors": e.errors}), on_error)

    def _on_query_success(self, result, on_success_callback):
        self._on_success(result)

        if on_success_callback:
            on_success_callback(result)

    def _on_query_error(self, result, on_error_callback):
        self._on_error(result)

        if on_error_callback:
            on_error_callback(result)

    def _on_success(self, result):
        if self.on_success:
            self.on_success(result)

    def _on_query(self):
        if self.on_query:
            self.on_query()

    def _on_error(self, result):
        if self.on_error:
            self.on_error(result)