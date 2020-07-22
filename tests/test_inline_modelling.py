"""Various tests to ensure inline (script) modelling works as expected."""

from e2e.common import modelling


def test_basic_modelling() -> None:
    """Ensure basic inline modelling works.

    Without using class-based modelling, `e2e` modelled constructs should be
    entirely functional. This only requires that the user manually supplies the
    parent.
    """

    root = modelling.NamedParentable("Root")
    leaf = modelling.NamedParentable("Leaf", parent=root)

    # Ensure these still behave as their components do
    assert root.name == "Root"
    assert leaf.name == "Leaf"

    # Ensure proper linkage
    assert root.parent is None
    assert leaf.parent == root
