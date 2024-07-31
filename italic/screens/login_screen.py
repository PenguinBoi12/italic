from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button, Label
from textual.containers import Container


class LoginScreen(Screen):
    CSS = """
    LoadingIndicator {
        color: #e83151
    }

    Button {
        margin: 1;
    }

    Input {
        margin: 1 0;
    }

    .banner {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: #e83151;
        text-style: bold;
    }

    #form {
        padding: 0 50;
    }
    """

    def compose(self) -> ComposeResult:
        self.email = Input(placeholder="Email")
        self.password = Input(placeholder="Password", password=True)

        yield Header()
        yield Footer()

        with Container():
            yield Label("Cursif", classes="banner")

            with Container(id="form"):
                yield self.email
                yield self.password
                yield Button("Login", id="submit")

    def on_mount(self) -> None:
        self.sub_title = "Login"

    @on(Button.Pressed, "#submit")
    async def submit(self) -> None:
        self.set_loading(True)

        query = """
            mutation Login($email: String!, $password: String!) {
                login(email: $email, password: $password) {
                    token
                    user {
                        username
                    }
                }
            }
        """

        result = await self.app.api.query(
            query,
            variables={
                "email": self.email.value, 
                "password": self.password.value
            }
        )

        if result.ok():
            username = result.login.user.username
            token = result.login.token

            self.notify(username, title="Welcome back!")
            self.dismiss(token)
        else:
            for error in result.errors:
                self.notify(error.message, title="Error", severity="error")

        self.set_loading(False)
