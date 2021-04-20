import pytest
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from kanon.units import Sexagesimal

from kanon_api.app import app


class TestApp:

    client = TestClient(app)

    @pytest.mark.parametrize(
        "date, expected",
        [
            ((1327, 7, 3), "1,47;18,48"),
            ((-2, 10, 3), "02,21 ; 49,32"),
            ((-2, -10, 3), HTTPException),
            ((-2, 10, 33), HTTPException),
        ],
    )
    def test_get_stp(self, date, expected):
        y, m, d = date
        response = self.client.get(f"/sun_true_pos?year={y}&month={m}&day={d}")

        if expected == HTTPException:
            assert response.status_code == 400

        else:
            content: dict = response.json()
            assert len(content) == 2
            assert Sexagesimal(content["value"]) == Sexagesimal(expected)
