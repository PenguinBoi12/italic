from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

from italic.screens.dashboard_screen import DashboardScreen
from italic.screens.login_screen import LoginScreen
from italic.api import CursifClient

from keyring import set_password, get_password, delete_password

KEYRING_SERVICE = "CURSIF"
KEYRING_NAME = "TOKEN"


class ItalicApp(App):
    CSS = """
        LoadingIndicator {
            color: #e83151
        }
    """

    BINDINGS = [
        Binding(
            key="ctrl+q",
            action="quit",
            description="Quit the app",
            priority=True,
            show=False
        ),
    ]

    @property
    def api(self):
        return CursifClient(
            self.token, 
            on_success=self.on_success, 
            on_query=self.on_query,
            on_error=self.on_error
        )

    @property
    def token(self):
        return get_password(KEYRING_SERVICE, KEYRING_NAME)

    @token.setter
    def token(self, token):
        set_password(KEYRING_SERVICE, KEYRING_NAME, token)

    @token.deleter
    def token(self):
        if self.token:
            delete_password(KEYRING_SERVICE, KEYRING_NAME)

    def compose(self) -> ComposeResult:
        self._client = None

        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Italic"

        if self.token:
            self.push_screen(DashboardScreen())
        else:
            self.push_screen(LoginScreen(), self.on_login)

    def on_login(self, token):
        self.token = token
        self.push_screen(DashboardScreen())

    def on_success(self, result):
        self.screen.set_loading(False)

    def on_query(self):
        self.screen.set_loading(True)

    def on_error(self, result):
        self.screen.set_loading(False)

        if any(e.status_code == 401 for e in result.errors):
            del self.token
            self.push_screen(LoginScreen())

        for error in result.errors:
            self.notify(error.message, title="Error", severity="error")