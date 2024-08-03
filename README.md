# Italic
Italic is a simple [Cursif](https://github.com/Code-Society-Lab/cursif) TUI client written in Python.

![image](https://github.com/user-attachments/assets/f87396ad-aa3a-4927-bd00-0269b83e0b47)


# Installation

## Prerequisites
1. Install Python 3.10 or higher.
https://www.python.org/downloads/

2. Clone the repo
```bash
$ git clone git@github.com:PenguinBoi12/italic.git
```

3. Create a virtual enviroment (recommended for dev)

```bash
$ virtualenv venv
$ source venv/bin/activate
```

https://peps.python.org/pep-0405/
https://virtualenv.pypa.io/en/latest/index.html

4. Install the dependencies and italic
```bash
$ pip install . 
```

Note: Use `-e` for development. 

# Usage
In your terminal simply run:
```bash
$ italic
```

You can also run the script manuall with: 
```bash
$ cd italic
$ python italic/
```

Login with your [Cursif](https://cursif.codesociety.xyz/) account. If you don't have an account create one at https://cursif.codesociety.xyz/register or via the [API](https://github.com/Code-Society-Lab/cursif-backend/wiki/GraphQL-API).

If you want to use another instance, like your own, you can change the api endpoint with `CURSIF_ENDPOINT`.
```bash
CURSIF_ENDPOINT=https://cursif.example.com/api
```

# Roadmap

- [ ] Register
- [X] Login
- [ ] Logout
- [ ] Credentials
  - [X] Save locally
  - [X] Delete locally
  - [ ] Toggle Remember me
- [ ] Notebook
  - [X] Select a notebook
  - [ ] Create a notebook
  - [ ] Delete a notebook
  - [ ] Update a notebook
- [X] Pages
  - [X] Create a page
  - [X] Rename a page
  - [X] Delete a page
  - [X] Edit the content of a page
  - [X] Markdown Preview
- [X] Proper error handling
 
