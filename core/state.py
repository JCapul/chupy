import logging
import weakref
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class _State:
    name: str = ""
    value: Any = None
    observers: set = field(default_factory=set)


def new_state(name=""):
    _state = _State(name)
    return StateValue(_state), StateSetter(_state)


class StateValue:
    def __init__(self, state: _State):
        self._state = state

    def __call__(self):
        return self._state.value

    def add_observer(self, callback):
        """Register an observer callback function."""
        self._state.observers.add(weakref.WeakMethod(callback))


class StateSetter:
    def __init__(self, state: _State):
        self._state = state

    def __call__(self, value_or_fn):
        if callable(value_or_fn):
            self._state.value = value_or_fn(self._state.value)
        else:
            self._state.value = value_or_fn
        self._notify_observers()

    def _notify_observers(self):
        """Notify all registered observers of a state change."""
        for observer_ref in list(self._state.observers):
            observer = observer_ref()
            if observer is not None:
                observer()
            else:
                # remove dead references
                self._state.observers.remove(observer_ref)
