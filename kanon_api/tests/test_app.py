import pytest
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from kanon.units import Sexagesimal

from kanon_api.app import app

sdate = (1327, 7, 3)


class TestApp:

    client = TestClient(app)

    @pytest.mark.parametrize(
        "planet, date, step, nval, result",
        [
            ("sun", sdate, 1, 1, "1,47;18,48"),
            ("sun", (10, 2, 13), 2, 4, "05,22 ; 36,47"),
            ("moon", sdate, 3, 1, "4,19;35,55"),
            ("saturn", sdate, 1, 1, "1,47;5,1"),
            ("venus", sdate, 1, 3, "2,1;27,13"),
            ("mercury", sdate, 1, 1, "2,13;5,1"),
            ("sun", (10, 52, 13), 1, 1, HTTPException),
        ],
    )
    def test_get_truepos(self, planet, date, nval, step, result):
        y, m, d = date

        with TestClient(app) as client:
            response = client.get(
                f"ephemerides/{planet}/true_pos",
                params={
                    "year": y,
                    "month": m,
                    "day": d,
                    "number_of_values": nval,
                    "step": step,
                },
            )

        if result == HTTPException:
            assert response.status_code == 400

        else:
            assert response.status_code == 200, response.text
            content: list[dict] = response.json()

            pos12h = Sexagesimal(content[0]["position"])

            assert pos12h == Sexagesimal(result)

            assert len(content) == nval

            assert all(
                val.get("jdn") - content[0].get("jdn") == step * idx
                for idx, val in enumerate(content)
            )

            with TestClient(app) as client:
                response6h = client.get(
                    f"ephemerides/{planet}/true_pos",
                    params={
                        "year": y,
                        "month": m,
                        "day": d,
                        "hours": 6,
                        "number_of_values": nval,
                        "step": step,
                    },
                )
                response13h30 = client.get(
                    f"ephemerides/{planet}/true_pos",
                    params={
                        "year": y,
                        "month": m,
                        "day": d,
                        "hours": 13,
                        "minutes": 30,
                        "number_of_values": nval,
                        "step": step,
                    },
                )

            pos6h = Sexagesimal(response6h.json()[0]["position"])
            pos13h30 = Sexagesimal(response13h30.json()[0]["position"])

            assert pos6h < pos12h < pos13h30

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
            assert len(content) == 2
            assert content["jdn"] == result
            assert isinstance(content["date"], str)

    @pytest.mark.parametrize(
        "input, result",
        [
            (("Julian A.D.", 2361658), [1753, 11, 13]),
            (("Julian A.D.", 2361658.1), [1753, 11, 13]),
            (("Julian A.D.", 2361658.6), [1753, 11, 14]),
            (("Arabic Civil Hijra", 2160836), [600, 5, 13]),
            (("Arabic Civil Hijra", 1735950), [-600, 5, 13]),
            (("Arabic Civil Hijra", 1735949.9), [-600, 5, 13]),
        ],
    )
    def test_get_from_jdn(self, input, result):
        calname, jdn = input
        response = self.client.get(f"calendars/{calname}/from_jdn", params={"jdn": jdn})

        assert response.status_code == 200
        content: dict = response.json()
        assert len(content) == 3
        assert content["ymd"] == result

    @pytest.mark.parametrize(
        "input, result",
        [
            (("Sexagesimal", 4.5, 2), "4;30"),
            (("Sexagesimal", 4.5, 1), "4;30"),
        ],
    )
    def test_get_from_float(self, input, result):

        radix, value, precision = input
        response = self.client.get(
            f"calculations/{radix}/from_float",
            params={"value": value, "precision": precision},
        )
        assert response.status_code == 200

        content: dict = response.json()
        br_result = Sexagesimal(result)
        assert Sexagesimal(content["value"]) == br_result.truncate()
        assert content["remainder"] == str(br_result.remainder)

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
        response = self.client.get(
            f"calculations/{radix}/to_float", params={"value": value}
        )

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

    def test_get_ascendant(self):
        response = self.client.get(
            "ephemerides/ascendant",
            params={"year": 1327, "month": 7, "day": 3, "latitude": 31},
        )

        assert response.status_code == 200
        assert response.json()["value"] == "03,16 ; 11,46"

        response = self.client.get(
            "ephemerides/ascendant",
            params={"year": 1327, "month": 7, "day": 3, "latitude": 34.8},
        )

        assert response.status_code == 200
        assert response.json()["value"] == "03,15 ; 42,00"

    def test_get_compute(self):
        response = self.client.get(
            "calculations/Sexagesimal/compute/", params={"query": "50;30,1 * 0;30"}
        )

        assert response.status_code == 200
        assert response.json()["value"] == "25 ; 15,00"
        assert response.json()["remainder"] == "0.5"

        response = self.client.get(
            "calculations/Sexagesimal/compute/", params={"query": "50;3a,1 * 0;30"}
        )

        assert response.status_code == 400

    def test_get_operations(self):
        response = self.client.get("calculations/Sexagesimal/sub/4;2/1;0,30")

        assert response.status_code == 200
        assert response.json()["value"] == "03 ; 01,30"

        response = self.client.get("calculations/Sexagesimal/sub/4;2/1;0,a30")

        assert response.status_code == 400

    def test_calendars_get_infos(self):
        response = self.client.get("calendars/Julian A.D./infos")

        assert response.status_code == 200
        data = response.json()

        assert data["common_year"] == 365
        assert data["months"][1]["days_cy"] == 28
        assert data["cycle"][0] == 3
