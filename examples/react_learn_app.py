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
from core import handler as h


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
    return html.div(
        [
            html.input(
                type="text",
                placeholder="Search...",
                name="search",
                x_handler=h(lambda value: set_search(value["search"]))
            ),
            html.div(
                [
                    html.input(
                        type="checkbox",
                        id="toto",
                        name="only_stock",
                        checked=True,
                        x_handler=h(lambda _: set_only_in_stock(lambda prev: not prev)),
                    ),
                    html.label("Only show products in stock", for_="toto"),
                ]
            ),
        ]
    )


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
    search, set_search = new_state()
    only_in_stock, set_only_in_stock = new_state()
    return html.div(
        [
            SearchBar(set_search, set_only_in_stock),
            ProductTable(search, only_in_stock),
        ]
    )


server = Server(FilterableProductTable)
