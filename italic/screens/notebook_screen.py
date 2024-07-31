from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, LoadingIndicator, Tabs, Tab
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

# Move all graphql stuff elsewhere
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from italic.widgets.editor import Editor

class NotebookScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close dashboar", show=False),
    ]

    def __init__(self, notebook_id, **kwargs):
        super().__init__(**kwargs)

        self.notebook_id = notebook_id
        self.notebook = None

    def compose(self) -> ComposeResult:
        self.tabs = Tabs()
        self.editor = Editor()

        yield Header()
        yield Footer()

        with Vertical(classes="container"):
            yield self.tabs
            yield self.editor


    async def on_mount(self) -> None:
        token = self.app.token
        transport = AIOHTTPTransport(url="https://api.codesociety.xyz/api", headers={'Authorization': f'Bearer {token}'})
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(
            """
              query GetNotebook($id: ID!) {
                notebook(id: $id) {
                  id
                  title
				  pages {
				    id
                    title
                 }
                }
              }
            """
        )

        self.set_loading(True)
        result = await client.execute_async(query, variable_values={"id": self.notebook_id})
        self.set_loading(False)

        self.notebook = result["notebook"]
        self.sub_title = self.notebook["title"]

        # move to function
        for page in self.notebook["pages"]:
            self.tabs.add_tab(Tab(page["title"], id=f"page_{page['id']}"))

        if self.tabs.tab_count > 0:
            self.editor.load(self.notebook["pages"][0]["id"])

    async def on_tabs_tab_activated(self, tab_activated):
        if self.tabs.tab_count > 0:
            page_id = tab_activated.tab.id.split("_")[1]
            self.editor.load(page_id)
