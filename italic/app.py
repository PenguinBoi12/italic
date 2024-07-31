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

    BINDINGS = [
        Binding(
            key="ctrl+q",
            action="quit",
            description="Quit the app",
            priority=True
        ),
        Binding(
            key="ctrl+question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        ),
    ]

    @property
    def token(self):
        return get_password(KEYRING_SERVICE, KEYRING_NAME)

    @token.setter
    def token(self, token):
        set_password(KEYRING_SERVICE, KEYRING_NAME, token)

    @token.deleter
    def token(self):
        delete_password(KEYRING_SERVICE, KEYRING_NAME)

    @property
    def api(self):
        return CursifClient(self.token)

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


if __name__ == '__main__':
    ItalicApp().run()
