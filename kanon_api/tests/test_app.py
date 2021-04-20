import pytest
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from kanon.units import Sexagesimal

from kanon_api.app import app


class TestApp:

    client = TestClient(app)

    @pytest.mark.parametrize(
        "input, result",
        [
            ((1327, 7, 3), "1,47;18,48"),
            ((10, 2, 13), "05,22 ; 36,47"),
            ((2, -10, 3), HTTPException),
        ],
    )
    def test_get_suntruepos(self, input, result):
        y, m, d = input
        response = self.client.get(
            "/sun_true_pos", params={"year": y, "month": m, "day": d}
        )

        if result == HTTPException:
            assert response.status_code == 400

        else:
            content: dict = response.json()
            assert len(content) == 2
            assert Sexagesimal(content["value"]) == Sexagesimal(result)

    @pytest.mark.parametrize(
        "input, result",
        [
            (("Julian A.D.", 1753, 11, 13), 2361658),
            (("Arabic Civil Hijra", -600, 5, 13), 1735689),
            (("Unknown", 2, 10, 3), HTTPException),
        ],
    )
    def test_get_date_jdn(self, input, result):
        calname, y, m, d = input
        response = self.client.get(
            "/date_jdn", params={"calendar": calname, "year": y, "month": m, "day": d}
        )

        if result == HTTPException:
            assert response.status_code == 400

        else:
            content: dict = response.json()
            assert len(content) == 1
            assert content["jdn"] == result

    @pytest.mark.parametrize(
        "input, result",
        [
            (("Julian A.D.", 2361658), [1753, 11, 13]),
            (("Arabic Civil Hijra", 2160836), [600, 5, 13]),
            (("Unknown", 25855555), HTTPException),
        ],
    )
    def test_get_jdn_date(self, input, result):
        calname, jdn = input
        response = self.client.get(
            "/jdn_date", params={"calendar": calname, "jdn": jdn}
        )

        if result == HTTPException:
            assert response.status_code == 400

        else:
            content: dict = response.json()
            assert len(content) == 1
            assert content["date"] == result

    @pytest.mark.parametrize(
        "input, result",
        [
            ((4.5, 2), "4;30"),
        ],
    )
    def test_get_float_sexa(self, input, result):
        value, precision = input
        response = self.client.get(
            "/float_sexa", params={"value": value, "precision": precision}
        )

        content: dict = response.json()
        assert len(content) == 1
        assert Sexagesimal(content["value"]) == Sexagesimal(result)

    @pytest.mark.parametrize(
        "input, result",
        [
            ("4;30", 4.5),
            ("-1;1", -1.0166666666666666),
            ("aa", HTTPException),
        ],
    )
    def test_get_sexa_float(self, input, result):
        response = self.client.get("/sexa_float", params={"value": input})

        if result == HTTPException:
            assert response.status_code == 400

        else:
            content: dict = response.json()
            assert len(content) == 1
            assert content["value"] == result
