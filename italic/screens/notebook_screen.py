from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Tabs, Tab, Input
from textual.containers import Vertical, Grid
from textual.binding import Binding
from textual import work

from italic.widgets.editor import Editor


class RenameModal(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close", show=False)
    ]

    CSS = """
	RenameModal {
    	align: center middle;
	}

	#dialog {
    	grid-size: 2;
    	grid-gutter: 1 2;
    	grid-rows: 1fr 3;
    	padding: 0 1;
    	width: 60;
    	height: 11;
    	border: thick $background 80%;
    	background: $surface;
        align: center middle;
	}

    #label_input {
		column-span: 2;
	}
    """

    def __init__(self, current_label):
        super().__init__()
        self.current_label = current_label

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            yield Input(value=self.current_label, id="label_input")

    def on_input_submitted(self, input):
        # add empty validation
        self.dismiss(input.value)


class NotebookScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close dashboard", show=False),

        # tabs binding
        Binding("ctrl+a", "add_tab", "Add new page"),
        Binding("ctrl+r", "rename_tab", "Rename page"),
        Binding("ctrl+d", "delete_tab", "Delete page"),
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

    async def action_add_tab(self):
        # change modal name?
        self.app.push_screen(RenameModal("Untitled Page"), self.on_tab_added)

    async def action_rename_tab(self):
        if self.tabs.tab_count > 0:
            active_tab_label = self.tabs.active_tab.label_text
            self.app.push_screen(RenameModal(active_tab_label), self.on_tab_renamed)

    @work(exclusive=True)
    async def action_delete_tab(self):
        if self.tabs.tab_count > 0:
            await self.on_tab_deleted(True)

    @work(exclusive=True)
    async def on_tab_added(self, title):
        query = """
            mutation CreatePage($title: String!, $parentId: ID!, $parentType: String!) {
                createPage(title: $title, parentId: $parentId, parentType: $parentType) {
                    id
                    title
                }
            }
        """

        result = await self.app.api.query(
            query,
            variables={
                "title": title,
                "parentId": self.notebook.id,
                "parentType": "notebook"
            }
        )

        self.tabs.add_tab(
            Tab(
                result.create_page.title,
                id=f"page_{result.create_page.id}"
            )
        )

    @work(exclusive=True)
    async def on_tab_renamed(self, value):
        self.tabs.active_tab.label = value
        page_id = self.tabs.active_tab.id.split("_")[1] # need a better way to handle ids

        query = """
            mutation UpdatePage($id: ID!, $title: String) {
                updatePage(id: $id, title: $title) {
                    title
                }
            }
        """

        await self.app.api.query(
            query,
            variables={
                "id": page_id,
                "title": value
            }
        )

    async def on_tab_deleted(self, confirmed):
        if not confirmed:
            return

        query = """
            mutation DeletePage($id: ID!) {
                deletePage(id: $id) {
                    id
                }
            }
        """

        result = await self.app.api.query(
            query,
            variables={
                "id": self.tabs.active_tab.id.split("_")[1],
            }
        )

        if result.ok():
            self.tabs.remove_tab(self.tabs.active_tab)
            self.editor.unload()
