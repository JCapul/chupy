from dataclasses import dataclass

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


@dataclass
class Product:
    price: str
    stocked: bool
    name: str


PRODUCTS = [
    Product(name="Apple", price="$1", stocked=True),
    Product(name="Dragonfruit", price="$1", stocked=True),
    Product(name="Dragonfruit", price="$2", stocked=False),
    Product(name="Spinach", price="$2", stocked=True),
    Product(name="Pumpkin", price="$4", stocked=False),
    Product(name="Peas", price="$1", stocked=True),
]


@component
def SearchBar(set_search: StateSetter, set_only_in_stock: StateSetter):
    @handler
    def handle_checkbox(_):
        set_only_in_stock(lambda prev: not prev)

    @handler
    def handle_search_input(value):
        set_search(value["search"])

    def layout():
        return html.div(
            [
                html.input(
                    type="text",
                    placeholder="Search...",
                    name="search",
                    x_handler=handle_search_input,
                ),
                html.div(
                    [
                        html.input(
                            type="checkbox",
                            id="toto",
                            name="only_stock",
                            checked=True,
                            x_handler=handle_checkbox,
                        ),
                        html.label("Only show products in stock", for_="toto"),
                    ]
                ),
            ]
        )

    return layout


@component
def ProductTable(product_filter: StateValue, only_in_stock: StateValue):
    @reload(on=[product_filter, only_in_stock])
    def layout():
        body = []
        for product in PRODUCTS:
            if only_in_stock() and not product.stocked:
                continue
            if product_filter() and not product.name.lower().startswith(
                product_filter().lower()
            ):
                continue
            if not product.stocked:
                name = html.span(product.name, style={"color": "red"})
            else:
                name = product.name

            body.append(html.tr([html.td(name), html.td(product.price)]))

        return html.table(
            [
                html.thead([html.tr([html.Th("Name"), html.Th("Price")])]),
                html.tbody(body),
            ],
        )

    return layout


@component
def FilterableProductTable():
    search, set_search = new_state("search")
    only_in_stock, set_only_in_stock = new_state("only_in_stock")

    def layout():
        return html.div(
            [
                SearchBar(set_search, set_only_in_stock),
                ProductTable(search, only_in_stock),
            ]
        )

    return layout


server = Server(FilterableProductTable)
