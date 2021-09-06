import pytest

from kanon_api.utils import StaticMeta


def test_staticmeta():
    class A(metaclass=StaticMeta):
        pass

    with pytest.raises(TypeError):
        A()
