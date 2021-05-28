import pytest
from kanon.units import Sexagesimal

from kanon_api.core.calculations.parser import parse


@pytest.mark.parametrize(
    "value, result",
    [
        ("1;2", "1;2"),
        ("1;2 + 3", "4;2"),
        ("+4;2 - 3", "1;2"),
        ("0;10 - 3", "-2;50"),
        ("1;2 -- 3;1", "4;3"),
        ("1;2 --+ 3;1", "4;3"),
        ("1;2,10 + 3;1", "4;3,10"),
        ("1;2 * 2", "2;4"),
        ("2;2 / 2", "1;1"),
        ("2;2 / 2 + 1", "2;1"),
        ("1;1 + 3 * 1;1", "4;4"),
        ("-1;1", "-1;1"),
        ("1;1a + 3 * 1;1", SyntaxError),
        ("1;1 + *3 * 1;1", SyntaxError),
        ("1;1 + 3 */ 1;1", SyntaxError),
    ],
)
def test_parse(value, result):
    if isinstance(result, str):
        parsed_number = parse(value, Sexagesimal)
        assert parsed_number == Sexagesimal(result)
    else:
        with pytest.raises(result) as err:
            parse(value, Sexagesimal)

        assert "Invalid syntax" in str(err.value)
