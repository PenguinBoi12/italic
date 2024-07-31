from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, LoadingIndicator

from italic.screens.notebook_screen import NotebookScreen

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

class DashboardScreen(Screen):
	def compose(self) -> ComposeResult:
		self.list_view = ListView()

		yield Header()
		yield Footer()
		yield self.list_view

	# Had to set async for the gql query
	async def on_list_view_selected(self, selection) -> None:
		item = selection.item
		self.app.push_screen(NotebookScreen(item.name, name=item.name))

	async def on_mount(self) -> None:
		self.set_loading(True)
		self.sub_title = "My notebooks"

		token = self.app.token
		transport = AIOHTTPTransport(url="https://api.codesociety.xyz/api", headers={'Authorization': f'Bearer {token}'})
		client = Client(transport=transport, fetch_schema_from_transport=True)

		query = gql(
            """
              query GetNotebooks {
                notebooks {
                  id
                  title
				  description
                }
              }
            """
		)

		result = await client.execute_async(query)

		for notebook in result["notebooks"]:
			self.list_view.append(ListItem(
				Static(f"=== {notebook['title']} ==="),
				Static(notebook['description'] or " "),
				name=notebook['id']
			))

		self.set_loading(False)
