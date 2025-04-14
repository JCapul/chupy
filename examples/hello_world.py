from core import (
    Server,
    StateSetter,
    StateValue,
    component,
    html,
    new_state,
    reload,
)
from core import (
    handler as h,
)


@component
def NameInput(set_name: StateSetter):
    return html.input(
        type="text",
        placeholder="your name",
        name="name",
        x_handler=h(lambda val: set_name(val["name"])),
    )


@component
def SayHello(name: StateValue):
    @reload(on=[name])
    def layout():
        return html.H4(f"Hello {name()}!") if name() else None

    return layout


@component
def ReactiveHelloWorld():
    name, set_name = new_state()
    return html.div([NameInput(set_name), SayHello(name)])


server = Server(ReactiveHelloWorld)
