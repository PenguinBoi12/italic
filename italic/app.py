from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Header, Footer

from keyring import set_password, get_password

from italic.screens.dashboard_screen import DashboardScreen
from italic.screens.login_screen import LoginScreen

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

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Italic"
        self.token = get_password("CURSIF", "TOKEN")

        if self.token:
            self.push_screen(DashboardScreen())
        else:
            self.push_screen(LoginScreen(), self.on_login)

    def on_login(self, token):
       	self.token = token
        set_password("CURSIF", "TOKEN", token)
        self.push_screen(DashboardScreen())

if __name__ == '__main__':
	ItalicApp().run()
