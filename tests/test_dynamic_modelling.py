"""Various tests to ensure dynamic (non-static) modelling is functional."""
# pylint: disable=missing-docstring,missing-class-docstring

from typing import Any
from unittest import mock

from e2e.common import modelling


def test_method_returned_modelling() -> None:
    """Ensure dynamic method-returned modelling works.

    Sometimes, you can't or don't want to make exact models for everything and
    they are parameterized (e.g. for list items). These are things you still
    want uniquely modelled, but the details are determined at test-time.

    Implicitly, this is expecting the framework to intercept the method's
    returned model to stitch the parent as the containing instance.
    """

    class SubModel(modelling.NamedParentable):
        leaf = modelling.NamedParentable("Leaf")

    class Model(modelling.NamedParentable):
        # pylint: disable=no-self-use  # intentional
        def sub_by_instance_method(self, label: str) -> SubModel:
            return SubModel("Sub by {}".format(label))

        @classmethod
        def sub_by_class_method(cls, label: str) -> SubModel:
            return SubModel("Sub by {}".format(label))

        @staticmethod
        def sub_by_static_method(label: str) -> SubModel:
            return SubModel("Sub by {}".format(label))

    m = Model("TestModel")

    assert m.sub_by_instance_method("foo-inst").parent == m
    assert m.sub_by_instance_method("bar-inst").parent == m

    assert (
        str(m.sub_by_instance_method("foo-inst").leaf)
        == "'Leaf' in 'Sub by foo-inst' in 'TestModel'"
    )
    assert (
        str(m.sub_by_instance_method("bar-inst").leaf)
        == "'Leaf' in 'Sub by bar-inst' in 'TestModel'"
    )

    # FIXME: Also test this with parent overrides

    # We can't support these; they don't make sense with the rest of how the
    # rest of the modelling framework works.
    assert m.sub_by_class_method("foo-cls").parent is None
    assert m.sub_by_class_method("bar-cls").parent is None
    assert m.sub_by_static_method("foo-static").parent is None
    assert m.sub_by_static_method("bar-static").parent is None


def test_other_methods_preserved() -> None:
    """Ensure other methods on models are not interrupted.

    Sometimes, it is desired to have helper methods on models to perform a
    series of actions or summarize some information. These should be left
    untouched so they operate as written.
    """

    class SubModel(modelling.NamedParentable):
        leaf = modelling.NamedParentable("Leaf")

    class Model(modelling.NamedParentable):
        sub = SubModel("TestSubModel")

        def interact_with_leaf(self) -> None:
            self.sub.leaf.do_action()  # type: ignore

        @property
        def ret_bool_prop(self) -> bool:
            return True

        # pylint: disable=no-self-use  # intentional
        def ret_bool_inst(self) -> bool:
            return True

        @classmethod
        def ret_bool_cls(cls) -> bool:
            return True

        @staticmethod
        def ret_bool_static() -> bool:
            return True

    # Access via class
    assert Model.ret_bool_cls() is True
    assert Model.ret_bool_static() is True

    m = Model("TestModel")

    # Access via instance
    assert m.ret_bool_prop is True
    assert m.ret_bool_inst() is True
    assert m.ret_bool_cls() is True
    assert m.ret_bool_static() is True

    m.sub.leaf.do_action = mock.Mock()  # type: ignore
    assert m.interact_with_leaf() is None  # type: ignore  # mypy over-assertion


def test_user_members_preserved() -> None:
    """Ensure other class/instance data on models are preserved.

    Sometimes, it is desired to have additional class members within a model
    for non-model data. These should not be touched by this framework, and
    continue to work as expected.
    """

    class SubModel(modelling.NamedParentable):
        leaf = modelling.NamedParentable("Leaf")

    class Model(modelling.NamedParentable):
        sub = SubModel("TestSubModel")
        class_data = "some class data"

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.instance_data = "some instance data"

    # Access via class
    assert Model.class_data == "some class data"

    m = Model("TestModel")

    # Access via instance
    assert m.sub.parent == m
    assert m.class_data == "some class data"
    assert m.instance_data == "some instance data"
