from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button, Label
from textual.containers import Container
from textual import work


class LoginScreen(Screen):
    CSS = """
        Button {
            margin: 1;
        }

        Input {
            margin: 1 0;
        }

        #banner {
            width: 100%;
            height: 5;
            content-align: center middle;
            background: #e83151;
            text-style: bold;
        }

        #form {
            width: 50;
        }

        .center-middle {
            align: center middle;
        }
    """

    def compose(self) -> ComposeResult:
        self.email = Input(placeholder="Email")
        self.password = Input(placeholder="Password", password=True)

        yield Header()
        yield Footer()

        yield Label("Cursif", id="banner")

        with Container(classes="center-middle"):
            with Container(id="form", classes="center-middle"):
                yield self.email
                yield self.password
                yield Button("Login", id="submit")

    def on_mount(self) -> None:
        self.sub_title = "Login"

    @on(Button.Pressed, "#submit")
    @work(exclusive=True)
    async def submit(self) -> None:
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

        def on_success(result):
            username = result.login.user.username
            token = result.login.token

            self.notify(username, title="Welcome back!")
            self.dismiss(token)

        await self.app.api.query(
            query,
            variables={
                "email": self.email.value, 
                "password": self.password.value
            },
            on_success=on_success
        )