from textual.app import ComposeResult
from textual.widgets import Markdown, TextArea
from textual.widget import Widget
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.binding import Binding
from textual import work


class Editor(Widget):
    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        self.page = None

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

    async def action_refresh(self):
        if self.page:
            self.load(self.page.id)

    @work(exclusive=True)
    async def load(self, page_id) -> None:
        query = """
            query GetPage($id: ID!) {
                page(id: $id) {
                    id
                    content
                }
            }
        """

        def on_success(result):
            self.page = result.page
            self.text_area.load_text(self.page.content or "")

        await self.app.api.query(
            query,
            variables={"id": page_id},
            on_success=on_success
        )

    def unload(self):
        self.page = None
        self.text_area.clear()

    @work(exclusive=True)
    async def save(self):
        query = """
            mutation UpdatePage($id: ID!, $content: String) {
                updatePage(id: $id, content: $content) {
                    id
                    content
                }
            }
        """

        def on_success(result):
            self.page = result.update_page

        await self.app.api.query(
            query,
            variables={
                "id": self.page.id,
                "content": self.text_area.text
            },
            on_success=on_success
        )
