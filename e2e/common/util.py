"""Utility functionality used within the `e2e.*` ecosystem."""
from typing import Any
from typing import List
from typing import Type
from typing import TypeVar

T = TypeVar("T")


def fqualname_of(obj: Any) -> str:
    """Gets the fully-qualified name for the given object."""
    return "{}.{}".format(obj.__class__.__module__, obj.__class__.__qualname__)


def fname_of(obj: Any) -> str:
    """Get the module-qualified path for the class.

    This will not properly communicate nested classes, functions, etc.
    """
    return "{}.{}".format(obj.__class__.__module__, obj.__class__.__name__)


def subclasses_of(cls: Type[T]) -> List[Type[T]]:
    """Fetch the whole subclass tree of the given class as a list.

    No ordering guarantee is provided within the list.
    """
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(subclasses_of(subclass))

    return all_subclasses
