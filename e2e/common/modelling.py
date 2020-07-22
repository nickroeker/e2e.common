"""Base functionality for modelling frameworks."""
__all__ = ["NamedParentable", "ParentableMeta"]


import functools
import types
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypeVar

from . import util

T = TypeVar("T")
T_P = TypeVar("T_P", bound="NamedParentable")


def make_prop(original_element: T_P) -> property:
    """Wraps the given object into a `property`."""

    def ret_contained_element(self: "NamedParentable") -> T_P:
        # FIXME: switch to using a ._parent_override here.
        # if original_element.parent is None:
        original_element.parent = self
        return original_element

    return property(ret_contained_element)


def make_prop_via(original_element: T_P, parent_property: property) -> property:
    """Wraps the given object into a `property`, assigning the given parent.

    The given parent must be a `property` object, i.e. `Class.property` and not
    `object.property` (since the latter would run and return from the property).
    """

    def ret_contained_element(self: "NamedParentable") -> T_P:
        original_element.parent = parent_property.__get__(self, type(self))
        return original_element

    return property(ret_contained_element)


def stitch_parent(func: Callable[..., T]) -> Callable[..., T]:
    """Decorate a method on a model to stitch the parent on return."""

    @functools.wraps(func)
    def wrapper(self: "NamedParentable", *args: Any, **kwargs: Any) -> T:
        ret = func(self, *args, **kwargs)
        if ret != self and isinstance(ret, NamedParentable):
            ret.parent = self
        return ret

    return wrapper


class ParentableMeta(type):
    """Metaclass which handles stitching parents into a parented class model.

    Basic (parent not specified) model constructs are wrapped in a `property`
    which sets the parent to the containing class.

    More complex (user-specified parent) constructs are also wrapped in a
    `property`, but their parent is assigned as other basic or complex
    properties. These parents are bound and computed on access.
    """

    # An improvement would be to generate these property mappings, get all their
    # values once, and use that as the model. This could use some caching
    # mechanism or perhaps render out a new instance, which likely requires the
    # implementing class to provide this behaviour on ``__new__``.

    def __new__(
        cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]
    ) -> Any:
        known_model_objects: Dict[str, Any] = {}
        known_model_properties: Dict[Any, property] = {}

        # First pass: Record known model constructs and initial property proxies
        for attr in namespace:
            candidate = namespace[attr]
            # if type(candidate).__class__ is cls:
            # FIXME: Is `cls` appropriate here? Probably not? Multi metaclass?
            if isinstance(candidate.__class__, cls):
                known_model_objects[attr] = candidate
                known_model_properties[candidate] = make_prop(candidate)

        # Second pass: Remap user-given parents, finalize other model constructs
        # FIXME: TBD if this depends on `namespace` being ordered. Probably.
        for attr in namespace:
            candidate = namespace[attr]
            # if type(candidate).__class__ is cls:
            if isinstance(candidate.__class__, cls):
                if candidate.parent is not None:
                    parent_prop = known_model_properties[candidate.parent]
                    namespace[attr] = make_prop_via(candidate, parent_prop)
                    known_model_properties[candidate] = namespace[attr]
                else:
                    # Delayed evaluation in case objects remapped above
                    namespace[attr] = known_model_properties[known_model_objects[attr]]

        # Decoration pass: Wrap user-defined methods to point the parent model.
        # This actually wraps the framework's methods too, so we have to be careful.
        for attr in namespace:
            candidate = namespace[attr]
            if isinstance(candidate, types.FunctionType) and not (
                attr.startswith("__") and attr.endswith("__")
            ):
                namespace[attr] = stitch_parent(namespace[attr])

        return super().__new__(cls, name, bases, namespace)


class NamedParentable(metaclass=ParentableMeta):
    """Provides auto-stitched parents for Object-Modelling frameworks.

    The instance containing an instance of this class will be accessible via
    the `parent` attribute, with the whole hierarchy of parents accessible via
    the `parent_chain` property.

    It is possible to have no parent, e.g. for a top-level object.

    This provides additional functionality for labelling objects. The string
    representation will include the parent hierarchy, and this can be utilised
    in logging for effective human-friendly inspection.

    Args:
        name: A human-friendly name, utlised for string representation and
            logging.

    Keyword Args:
        parent: Optional explicit parent override, if desired.
    """

    name: str = "UNKNOWN"
    parent: Optional["NamedParentable"] = None

    def __init__(
        self, name: str, *, parent: Optional["NamedParentable"] = None,
    ):
        self.name = name
        self.parent = parent

    @property
    def parent_chain(self) -> List["NamedParentable"]:
        """Returns a list of parents in order of increasing distance."""
        return [self.parent] + self.parent.parent_chain if self.parent else []

    def __repr__(self) -> str:
        return "{}(name={})".format(util.fqualname_of(self), self.name)

    def __str__(self) -> str:
        return " in ".join([repr(p.name) for p in [self] + self.parent_chain])
