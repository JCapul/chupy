import logging
import weakref
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Callable

from core.html import render

logger = logging.getLogger(__name__)

_ctx_holder = ContextVar("_ctx_holder", default=None)

@dataclass
class _ContextState:
    root_component: None = None
    id_sequence: int = 0
    state_vars: list = field(default_factory=list)
    handlers: dict[str, Callable] = field(default_factory=dict)
    updates: set = field(default_factory=set)


class _HandlerWrapper:
    def __init__(self, handler_fn: Callable, uid: str):
        self._handler_fn = handler_fn
        self._uid = uid

    def __call__(self, *args, **kwargs):
        return self._handler_fn(*args, **kwargs)
    
    def __str__(self):
        # when assigned to a 'fx_action' in a layout function, rendering as str() will return its ID
        return self._uid

class _Context:
    
    @property
    def _ctx(self) -> _ContextState:
        _ctx = _ctx_holder.get()
        if _ctx is None:
            raise Exception("context can only be used within a Component function")
        return _ctx
    
    def initialize(self, root_component_factory) -> None:
        _ctx = _ContextState()
        _ctx_holder.set(_ctx)
        # NOTE: root_component_factory cannot be called before a frist context is set
        # since it may require a ctx to already be setup (e.g. to instanciate handlers)
        _ctx.root_component = root_component_factory()
    
    def new_id(self) -> str:
        _new_id = self._ctx.id_sequence
        self._ctx.id_sequence += 1 
        return str(_new_id)

    def register_handler(self, handler_fn: Callable) -> Callable:
        handler_id = f"{handler_fn.__name__}-{self.new_id()}"
        if hasattr(handler_fn, "__self__"):
            # bound method
            self._ctx.handlers[handler_id] = weakref.WeakMethod(handler_fn)
        else:
            self._ctx.handlers[handler_id] = weakref.ref(handler_fn)
        return _HandlerWrapper(handler_fn, handler_id)

    def process_msg(self, msg: dict):
        handler_id, args = msg["action"], msg["data"]
        if handler_id == "__init":
            return [("swap", "body", "outerHTML", render(self._ctx.root_component))]
        self._dispatch_handler(handler_id, args)
        return self._pull_updates()

    def _dispatch_handler(self, uid: str, data) -> None:
        handler_ref = self._ctx.handlers[uid]
        handler = handler_ref()
        if handler is None:
            logger.error("dead handler reference ('%s')", handler_ref)
            del self._ctx.handlers[uid]
        else:
            handler(data)

    def push_update(self, component) -> None:
        self._ctx.updates.add(weakref.ref(component))

    def _pull_updates(self) -> list:
        updates = []
        for component_ref in self._ctx.updates:
            component = component_ref()
            if component is None:
                logger.debug("update for a dead component reference (%s)", component_ref)
                # this may be possible if a state var update leads to a component to reload, but another state vars
                # update lead to an ancestor component to reload and replacing/removing this component
                continue
            update = component.reload_layout()
            updates.append(update)
        self._ctx.updates.clear()
        return updates


ctx = _Context()


# Public API

handler = ctx.register_handler
new_id = ctx.new_id