from __future__ import annotations


class HTMLTag:
    def __init__(self, tag_name: str, children: str|HTMLTag|list[HTMLTag]|None, **attrs):
        self._tag_name = tag_name
        if isinstance(children, (str, HTMLTag)):
            self.children = [children]
        elif children is None:
            self.children = []
        else:
            self.children = children
        self.attrs = attrs

    def _process_attrs(self) -> str:
        attrs = []
        for key, value in self.attrs.items():
            key = key.removesuffix("_").replace("_", "-")
            if isinstance(value, bool):
                attrs.append(key)
            else:
                attrs.append(f'{key}="{value}"')
        return " ".join(attrs)
            

    def __str__(self):
        attrs_str = self._process_attrs()
        inner_html = "".join(str(child) for child in self.children)
        return (
            f"<{self._tag_name} {attrs_str}>{inner_html}</{self._tag_name}>"
            if attrs_str else f"<{self._tag_name}>{inner_html}</{self._tag_name}>"
        )

class HTMLFactory:
    def __getattr__(self, tag_name):
        return lambda children=None, **attrs: HTMLTag(tag_name, children, **attrs)


html = HTMLFactory()

def render(html_obj: HTMLTag) -> str:
    return str(html_obj)

# Example usage
if __name__ == "__main__":
    example = html.div([html.p("Hello World"), html.foo("toto")], style="color: red;", class_="text-bold")
    print(render(example))  # Output: <div style="color: red;" class="text-bold"><p>Hello World</p><foo>toto</foo></div>
