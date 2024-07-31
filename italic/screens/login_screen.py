from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button, Label
from textual.containers import Container

# Move all graphql stuff elsewhere
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from keyring import set_password, get_password

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

		token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJjdXJzaWYiLCJleHAiOjE3MjI1NDAwNDcsImlhdCI6MTcyMjI4MDg0NywiaXNzIjoiY3Vyc2lmIiwianRpIjoiOGUyN2I3NjgtMDBlMi00NDJiLThlMDItYmQ0M2QxYWY4OTllIiwibmJmIjoxNzIyMjgwODQ2LCJzdWIiOiI0ZjQxZjNkMS1lYjhhLTQ0YzktYjUzOS0zZTYzYmQ5MDdhMzUiLCJ0eXAiOiJhY2Nlc3MifQ.cvOAxqFSZ_KZ70NQLtSCkV_f6indSCeVKVB6Nl8QBlQgFCz9lTiASWvOSj2On0RgO9xvWDzjkZj1wpk8YoYaCQ"
		transport = AIOHTTPTransport(url="https://api.codesociety.xyz/api", headers={'Authorization': f'Bearer {token}'})
		client = Client(transport=transport, fetch_schema_from_transport=True)

		query = gql(
            """
              mutation Login($email: String!, $password: String!) {
                login(email: $email, password: $password) {
                  token
				  user {
					username
				  }
                }
              }
            """
		)

		try:
			result = await client.execute_async(
				query,
				variable_values={"email": self.email.value, "password": self.password.value}
			)

			username = result["login"]["user"]["username"]
			token = result["login"]["token"]

			self.notify(f"Welcome back {username}!")
			self.dismiss(token)
		except Exception as exception:
			message = ", ".join(map(lambda e: e["message"], exception.errors))
			self.notify(message, title="Error", severity="error")
		finally:
			self.set_loading(False)
