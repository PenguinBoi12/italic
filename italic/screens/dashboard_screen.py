from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, ListView, ListItem, Static

from italic.screens.notebook_screen import NotebookScreen


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
        self.sub_title = "My notebooks"

        query = """
          query GetNotebooks {
            notebooks {
              id
              title
              description
            }
          }
        """

        def on_success(result):
            for notebook in result.notebooks:
                self.list_view.append(
                    ListItem(
                        Static(f"=== {notebook.title} ==="),
                        Static(notebook.description or " "),
                        name=notebook.id
                    )
                )

        await self.app.api.query(query, on_success=on_success)