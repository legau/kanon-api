import pytest
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from kanon.units import Sexagesimal

from kanon_api.app import app


class TestApp:

    client = TestClient(app)

    @pytest.mark.parametrize(
        "planet, date, result",
        [
            ("sun", (1327, 7, 3), "1,47;18,48"),
            ("sun", (10, 2, 13), "05,22 ; 36,47"),
            ("sun", (10, 52, 13), HTTPException),
            ("saturn", (2, 10, 3), HTTPException),
        ],
    )
    def test_get_truepos(self, planet, date, result):
        y, m, d = date
        response = self.client.get(
            f"ephemerides/{planet}/true_pos", params={"year": y, "month": m, "day": d}
        )

        if result == HTTPException:
            assert response.status_code == 400

        else:
            assert response.status_code == 200
            content: dict = response.json()
            assert len(content) == 2
            assert Sexagesimal(content["value"]) == Sexagesimal(result)

    @pytest.mark.parametrize(
        "input, result",
        [
            (("Julian A.D.", 1753, 11, 13), 2361658),
            (("Arabic Civil Hijra", -600, 5, 13), 1735950),
            (("Julian A.D.", 2, 50, 3), HTTPException),
        ],
    )
    def test_get_to_jdn(self, input, result):
        calname, y, m, d = input
        response = self.client.get(
            f"calendars/{calname}/to_jdn",
            params={"year": y, "month": m, "day": d},
        )

        if result == HTTPException:
            assert response.status_code == 400

        else:
            assert response.status_code == 200
            content: dict = response.json()
            assert len(content) == 1
            assert content["jdn"] == result

    @pytest.mark.parametrize(
        "input, result",
        [
            (("Julian A.D.", 2361658), [1753, 11, 13]),
            (("Arabic Civil Hijra", 2160836), [600, 5, 13]),
            (("Arabic Civil Hijra", 1735950), [-600, 5, 13]),
        ],
    )
    def test_get_from_jdn(self, input, result):
        calname, jdn = input
        response = self.client.get(f"calendars/{calname}/from_jdn", params={"jdn": jdn})

        assert response.status_code == 200
        content: dict = response.json()
        assert len(content) == 2
        assert content["ymd"] == result

    @pytest.mark.parametrize(
        "input, result",
        [(("Sexagesimal", 4.5, 2), "4;30")],
    )
    def test_get_from_float(self, input, result):

        radix, value, precision = input
        response = self.client.get(
            f"radices/{radix}/from_float",
            params={"value": value, "precision": precision},
        )
        assert response.status_code == 200

        content: dict = response.json()
        assert len(content) == 2
        assert Sexagesimal(content["value"]) == Sexagesimal(result)

    @pytest.mark.parametrize(
        "input, result",
        [
            (("Historical", "8s5;30"), 245.5),
            (("Sexagesimal", "-1;1"), -1.0166666666666666),
            (("Sexagesimal", "aa"), HTTPException),
        ],
    )
    def test_get_to_float(self, input, result):
        radix, value = input
        response = self.client.get(f"radices/{radix}/to_float", params={"value": value})

        if result == HTTPException:
            assert response.status_code == 400

        else:
            assert response.status_code == 200
            content: dict = response.json()
            assert len(content) == 1
            assert content["value"] == result

    def test_health_check(self):
        response = self.client.get("health")
        assert response.status_code == 200
