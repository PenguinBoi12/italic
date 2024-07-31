from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from re import sub


class Result:
    def __init__(self, data):
        self.errors = []

        for name, value in data.items():
            setattr(self, self._format_name(name), self._wrap(value))

    def ok(self):
        return len(self.errors) == 0

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Result(value) if isinstance(value, dict) else value

    def _format_name(self, name):
        return sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


class CursifClient:
    CURSIF_ENDPOINT = "https://api.codesociety.xyz/api"

    def __init__(self, token):
        self.token = token
        self._client = None

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

    async def query(self, query, variables={}) -> Result:
        try:
            result = await self.client.execute_async(
                gql(query),
                variable_values=variables
            )

            return Result(result)
        except Exception as exception:
            return Result({"errors": exception.errors})
