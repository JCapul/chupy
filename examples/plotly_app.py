import plotly.graph_objects as go

from core import (
    Server,
    StateSetter,
    StateValue,
    component,
    handler,
    html,
    new_state,
    reload,
)


@component
def TitleInput(set_title: StateSetter):
    @handler
    def handle_title_input(value):
        set_title(value["title"])

    def layout():
        return html.div(
            [
                html.input(
                    type="text",
                    placeholder="Type a title",
                    name="title",
                    x_handler=handle_title_input,
                ),
            ]
        )

    return layout


@component
def PlotlyFigureExample(title: StateValue):
    fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))

    @reload(on=[title])
    def layout():
        if title() is not None:
            fig.update_layout(title=title())
        return html.script(fig.to_json(), x_plotly="figure", type="application/json")

    return layout


@component
def MyPlotlyApp():
    title, set_title = new_state("title")

    def layout():
        return html.div([TitleInput(set_title), PlotlyFigureExample(title)])

    return layout


server = Server(MyPlotlyApp)
