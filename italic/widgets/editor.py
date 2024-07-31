from textual.app import ComposeResult, RenderResult
from textual.widgets import Markdown, TextArea, LoadingIndicator
from textual.widget import Widget
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual import work

# Move all graphql stuff elsewhere
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


class Editor(Widget):
    BINDINGS = [
		("ctrl+s", "save", "Save"),
		("ctrl+r", "refresh", "Refresh"),
		("ctrl+n", "rename", "Rename Page"),
	]

    def __init__(self):
        super().__init__()
        self.page = None

    def compose(self) -> ComposeResult:
        self.text_area = TextArea("", language="markdown")
        self.preview = Markdown(self.text_area.text)

        with Horizontal():
            with Vertical():
                yield self.text_area
            with VerticalScroll():
                yield self.preview

    def on_text_area_changed(self) -> None:
        self.preview.update(self.text_area.text)

    async def action_save(self):
        if self.page:
            self.save()

    async def action_rename(self):
        if self.page:
            self.page["title"] = "new name"
            self.save()

    async def action_refresh(self):
        if self.page:
            self.load(self.page["id"])

    @work(exclusive=True)
    async def load(self, page_id) -> None:
        token = self.app.token
        transport = AIOHTTPTransport(url="https://api.codesociety.xyz/api", headers={'Authorization': f'Bearer {token}'})
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(
            """
              query GetPage($id: ID!) {
                page(id: $id) {
                  id
                  title
                  content
                }
              }
            """
        )

        result = await client.execute_async(query, variable_values={"id": page_id})

        self.page = result["page"]
        self.sub_title = self.page["title"]

        self.text_area.load_text(self.page["content"])

    @work(exclusive=True)
    async def save(self):
        token = self.app.token
        transport = AIOHTTPTransport(url="https://api.codesociety.xyz/api", headers={'Authorization': f'Bearer {token}'})
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(
            """
              mutation UpdatePage($id: ID!, $title: String, $content: String) {
                updatePage(id: $id, title: $title, content: $content) {
                  id
                  title
                  content
                }
              }
            """
        )

        result = await client.execute_async(
            query,
            variable_values={
                "id": self.page["id"],
                "title": self.page["title"],
                "content": self.text_area.text
            }
        )

        self.page = result["updatePage"]
        self.sub_title = self.page["title"]
