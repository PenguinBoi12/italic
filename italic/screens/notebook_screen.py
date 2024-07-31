from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Tabs, Tab
from textual.containers import Vertical
from textual.binding import Binding

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
        self.set_loading(True)

        query = """
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

        result = await self.app.api.query(
            query,
            variables={"id": self.notebook_id}
        )

        self.notebook = result.notebook
        self.sub_title = result.notebook.title

        for page in self.notebook.pages:
            self.tabs.add_tab(Tab(page.title, id=f"page_{page.id}"))

        self.set_loading(False)

    async def on_tabs_tab_activated(self, tab_activated):
        if self.tabs.tab_count > 0:
            self.editor.load(tab_activated.tab.id.split("_")[1])