# 🐣 chupy — toying with python frontend development

*A place where the python frontend I want can hatch*

Primarily a learning experience, this is an attempt at building a minimalist reactive single-page app toolkit in python. It's a crowded space, I know.

Here is an opinionated set of features I manage to make it work so far:
- write HTML in pure python, no template, no DSL, no restricted construct, just python but all python
- state managed in the server using React-like state objects and reactive components
- besides fast coms and possibility for streaming updates, it uses a sticky websocket connection between client and server to keep all state in server's memory
- a core of 50 lines of javascript to send user interactions and manage DOM updates adapted from the awesome [fixi.js](https://github.com/bigskysoftware/fixi), that's it


## Getting started

```shell
$ uv sync --group dev --all-extras
$ uv run uvicorn --reload examples.react_learn_app:server
```