# Exemple of a component
import logging
from functools import wraps, cached_property

from core.context import ctx
from core.state import StateValue

logger = logging.getLogger(__name__)


class _Component:
    def __init__(self, name, layout):
        self._name = name
        self._layout_fn = layout if callable(layout) else lambda: layout
        if hasattr(layout, "__dependencies__"):
            for state_val in layout.__dependencies__:
                state_val.add_observer(self.should_reload)
        self._tree = None
        # TODO: add equivalent of strict mode that checks layout function is somewhat pure
        # -> execute layout function twice and check output is same (especially UID is defined in component scope not in layout func)
        # -> no state vars mutation (should not use set_X function)
        self.reload_layout()

    def reload_layout(self):
        self._tree = self._layout_fn()
        #TODO: is the tree first component always a HTMLTag object ? or can it also be a _Component ? 
        # but what's the purpose of having a component which layout returns another component...
        if not self._tree.attrs.get("id"):
            # assign to the root element the component lazily-generated Id if none given by the user
            self._tree.attrs["id"] = self._id

        # TODO: this function could ouptut a patch object that would encode the diffs
        # to make versus previous layout/tree, need to implement a diff algo
        return ("swap", self.id, "outerHTML", str(self))

    @cached_property
    def _id(self):
        """Lazily generate a new id, only once per component instance and only if needed."""
        return f"{self._name}-{ctx.new_id()}"

    @property
    def id(self) -> str:
        """Return the tree root element ID."""
        # TODO: this can be another Component or HTMLTag
        return self._tree.attrs["id"]

    def should_reload(self):
        ctx.push_update(self)

    def __str__(self) -> str:
        return str(self._tree)


# Public API

def component(component_fn):
    @wraps(component_fn)
    def wrapper(*args, **kwargs):
        layout_fn = component_fn(*args, **kwargs)
        return _Component(component_fn.__name__, layout_fn)

    return wrapper


def reload(on: list[StateValue]):
    def decorator(render_fn):
        render_fn.__dependencies__ = on
        return render_fn

    return decorator
