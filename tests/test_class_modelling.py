"""Various tests to ensure class-based modelling works as expected."""
# pylint: disable=missing-docstring,protected-access

from e2e.common import modelling


def test_basic_class_linkage() -> None:
    """Ensure that class modelling links the containing class as the parent.

    If no parent is specified, the containing instance should be the parent.
    """

    class Model(modelling.NamedParentable):
        leaf = modelling.NamedParentable("Leaf")

    m = Model("TestModel")

    assert m.leaf.parent == m
    assert m.parent is None


def test_hidden_class_linkage() -> None:
    """Ensure that overriding parents via class modelling works as expected.

    If a parent is specified, it should be used.
    """

    class Model(modelling.NamedParentable):
        _hidden = modelling.NamedParentable("Hidden")
        leaf = modelling.NamedParentable("Leaf", parent=_hidden)

    m = Model("TestModel")

    assert m.leaf.parent != m
    assert m.leaf.parent == m._hidden


def test_deeply_hidden_class_linkage() -> None:
    """Ensure that overriding parents via class modelling works as expected.

    If a parent is specified, it should be used, no matter how deep the override
    structure goes.
    """

    class Model(modelling.NamedParentable):
        _hidden_top = modelling.NamedParentable("_Top")
        _hidden_middle = modelling.NamedParentable("_Middle", parent=_hidden_top)
        _hidden_bottom = modelling.NamedParentable("_Bottom", parent=_hidden_middle)
        leaf = modelling.NamedParentable("Leaf", parent=_hidden_bottom)

    m = Model("TestModel")

    assert m.leaf.parent_chain == [
        m._hidden_bottom,
        m._hidden_middle,
        m._hidden_top,
        m,
    ]
    assert m._hidden_bottom.parent_chain == [
        m._hidden_middle,
        m._hidden_top,
        m,
    ]


def test_nested_models() -> None:
    """Ensure users are able to nest their own models."""

    class SubModel(modelling.NamedParentable):
        leaf = modelling.NamedParentable("Leaf")

    class Model(modelling.NamedParentable):
        sub = SubModel("TestSubModel")

    m = Model("TestModel")

    assert m.sub.parent == m
    assert m.sub.leaf.parent == m.sub


def test_clobbered_custom_models() -> None:
    """Ensure users are able to create their own models, even ignoring rules.

    While it is best to call `__init__`, etc. when extending frameworks, some
    don't. Additionally, sometimes they're simply called incorrectly. The
    framework is designed to be resilient to this abuse.

    This ensures the framework functions (delegates parents correctly), not
    necessarily that nice-to-haves (logging) work optimally.
    """

    class ClobberedModel(modelling.NamedParentable):
        # pylint: disable=super-init-not-called
        def __init__(self) -> None:
            self.custom_data = "foo"

        leaf = modelling.NamedParentable("Leaf")

    class Model(modelling.NamedParentable):
        clobbered = ClobberedModel()

    m = Model("TestModel")

    assert m.clobbered.leaf.parent_chain == [m.clobbered, m]


def test_manual_parent_override() -> None:
    """Ensure that users can override the parent in a `property`, if so desired.

    This case shouldn't be widely used, but should function as it is natural to
    assume it will work.
    """

    class Model(modelling.NamedParentable):
        _hidden = modelling.NamedParentable("Hidden")

        @property
        def leaf(self) -> modelling.NamedParentable:
            return modelling.NamedParentable("Leaf", parent=self._hidden)

    m = Model("TestModel")

    assert m.leaf.parent != m
    assert m.leaf.parent == m._hidden


def test_equal_definitions_are_separately_constructed() -> None:
    """Ensure otherwise equal children are both functional.

    This exists in case remapping via the metaclass ends up substituting (or
    leaving alone) an element in case of matching selectors and type (or the
    otherwise current definition of equality). Sometimes this is desired for
    logically different areas of the model that happen to have the same
    selector for now.

    Ensuring they are separate objects is best, since this ensures they were
    respected during construction. Equality is not the same, though.
    """

    class Model(modelling.NamedParentable):
        leaf1 = modelling.NamedParentable("Leaf")
        leaf2 = modelling.NamedParentable("Leaf")

    m = Model("TestModel")

    assert m.leaf1.parent == m
    assert m.leaf2.parent == m

    assert m.leaf1 is not m.leaf2


def test_equal_definitions_are_separately_constructed_middleman() -> None:
    """Same as previous test, but for deeper linkage."""

    class SubModel(modelling.NamedParentable):
        leaf = modelling.NamedParentable("Leaf")

    class Model(modelling.NamedParentable):
        sub1 = SubModel("Sub1")
        sub2 = SubModel("Sub2")

    m = Model("TestModel")

    assert m.sub1.leaf.parent == m.sub1
    assert m.sub2.leaf.parent == m.sub2


# FIXME: Test w/ user Model that injects another Metaclass (e.g. Generic[T])
