import pytest
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from kanon.models.models import equ_of_the_sun, planet_double_arg_mercury
from kanon.units import Sexagesimal

from kanon_api.app import app

sdate = (1327, 7, 3)

client = TestClient(app)


@pytest.mark.parametrize(
    "ts, planet, date, step, nval, result",
    [
        ("parisian_alphonsine_tables", "sun", sdate, 1, 1, "1,47;18,48"),
        ("parisian_alphonsine_tables", "sun", (10, 2, 13), 2, 4, "05,22 ; 56,25"),
        ("parisian_alphonsine_tables", "moon", sdate, 3, 1, "4,19;35,55"),
        ("parisian_alphonsine_tables", "saturn", sdate, 1, 1, "1,47;5,1"),
        ("parisian_alphonsine_tables", "venus", sdate, 1, 3, "2,1;27,13"),
        ("parisian_alphonsine_tables", "mercury", sdate, 1, 1, "2,13;5,1"),
        ("parisian_alphonsine_tables", "sun", (10, 52, 13), 1, 1, HTTPException),
    ],
)
def test_get_truepos(ts, planet, date, nval, step, result):
    y, m, d = date

    with TestClient(app) as client:
        response = client.get(
            f"ephemerides/{ts}/{planet}/true_pos",
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
        return

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
            f"ephemerides/{ts}/{planet}/true_pos",
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
            f"ephemerides/{ts}/{planet}/true_pos",
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
def test_get_to_jdn(input, result):
    calname, y, m, d = input
    response = client.get(
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
def test_get_from_jdn(input, result):
    calname, jdn = input
    response = client.get(f"calendars/{calname}/from_jdn", params={"jdn": jdn})

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
def test_get_from_float(input, result):

    radix, value, precision = input
    response = client.get(
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
def test_get_to_float(input, result):
    radix, value = input
    response = client.get(f"calculations/{radix}/to_float", params={"value": value})

    if result == HTTPException:
        assert response.status_code == 400

    else:
        assert response.status_code == 200
        content: dict = response.json()
        assert len(content) == 1
        assert content["value"] == result


def test_health_check():
    response = client.get("health")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "ts, result0, result1",
    [("parisian_alphonsine_tables", "03,16 ; 11,46", "03,15 ; 42,00")],
)
def test_get_ascendant(ts, result0, result1):
    response = client.get(
        f"ephemerides/{ts}/ascendant",
        params={"year": 1327, "month": 7, "day": 3, "latitude": 31},
    )

    assert response.status_code == 200
    assert response.json()["value"] == result0

    response = client.get(
        f"ephemerides/{ts}/ascendant",
        params={"year": 1327, "month": 7, "day": 3, "latitude": 34.8},
    )

    assert response.status_code == 200
    assert response.json()["value"] == result1


def test_get_compute():
    response = client.get(
        "calculations/Sexagesimal/compute/", params={"query": "50;30,1 * 0;30"}
    )

    assert response.status_code == 200
    assert response.json()["value"] == "25 ; 15,00"
    assert response.json()["remainder"] == "0.5"

    response = client.get(
        "calculations/Sexagesimal/compute/", params={"query": "50;3a,1 * 0;30"}
    )

    assert response.status_code == 400


def test_get_operations():
    response = client.get("calculations/Sexagesimal/sub/4;2/1;0,30")

    assert response.status_code == 200
    assert response.json()["value"] == "03 ; 01,30"

    response = client.get("calculations/Sexagesimal/sub/4;2/1;0,a30")

    assert response.status_code == 400


def test_calendars_get_infos():
    response = client.get("calendars/Julian A.D./infos")

    assert response.status_code == 200
    data = response.json()

    assert data["common_year"] == 365
    assert data["months"][1]["days_cy"] == 28
    assert data["cycle"][0] == 3


@pytest.mark.parametrize(
    "ts, result0, result11, result10",
    [("parisian_alphonsine_tables", "03,16 ; 11,46", "02,46 ; 34,47", "02,15 ; 00,47")],
)
def test_houses(ts, result0, result11, result10):
    response = client.get(
        f"ephemerides/{ts}/houses",
        params={"year": 1327, "month": 7, "day": 3, "latitude": 31},
    )

    assert response.status_code == 200
    assert len(response.json()) == 12
    assert response.json()[0] == result0
    assert response.json()[11] == result11

    response = client.get(
        f"ephemerides/{ts}/houses",
        params={
            "year": 1327,
            "month": 7,
            "day": 3,
            "latitude": 31,
            "method": "M1",
        },
    )

    assert response.json()[10] == result10


def test_get_model():
    response = client.get("models/39")
    assert response.status_code == 200
    assert response.json() == {
        "args": 1,
        "params": [106, 107],
        "table_type": "equ_anomaly_at_max_dist",
        "table_type_id": 72,
        "model_name": "equ_of_anomaly_mercury_at_great_dist",
    }

    response = client.get("models/1002")
    assert response.status_code == 404


def test_fill_model():
    arg1 = list(range(10))
    response = client.post(
        f"models/{equ_of_the_sun.formula_id}/fill/",
        json={
            "arg1": arg1,
            "params": {"50": 1},
            "displacement": [0, 0, 0],
        },
    )
    assert response.status_code == 200
    assert response.json() == [equ_of_the_sun(x, 1) for x in arg1]

    arg2 = list(range(3))
    response = client.post(
        f"models/{planet_double_arg_mercury.formula_id}/fill/",
        json={
            "arg1": arg1,
            "arg2": arg2,
            "params": {"124": 1, "125": 2},
            "displacement": [0, 0, 0],
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        planet_double_arg_mercury(x, y, 1, 2) for y in arg2 for x in arg1
    ]

    response = client.post(
        f"models/{planet_double_arg_mercury.formula_id}/fill/",
        json={
            "arg1": arg1,
            "arg2": arg2,
            "params": {"124": None, "125": 2},
            "displacement": [0, 0, 0],
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Null parameter"}


def test_estimate_parameter():
    arg1 = list(range(30))
    entries = [equ_of_the_sun(x, 1) for x in arg1]
    entries[5] = entries[11] = entries[13] = None
    response = client.post(
        f"models/{equ_of_the_sun.formula_id}/estimate/",
        json={
            "entries": entries,
            "arg1": arg1,
            "params": {"50": None},
            "displacement": [0, 0, 0],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"50": 1}

    arg2 = list(range(5))
    entries = [planet_double_arg_mercury(x, y, 1, 2) for y in arg2 for x in arg1]
    entries[6] = None
    response = client.post(
        f"models/{planet_double_arg_mercury.formula_id}/estimate/",
        json={
            "arg1": arg1,
            "arg2": arg2,
            "entries": [
                planet_double_arg_mercury(x, y, 1, 2) for y in arg2 for x in arg1
            ],
            "params": {"124": None, "125": None},
            "displacement": [0, 0, 0],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"124": 1, "125": 2}

    response = client.post(
        f"models/{planet_double_arg_mercury.formula_id}/estimate/",
        json={
            "arg1": arg1,
            "arg2": arg2,
            "entries": [0, 1, 2],
            "params": {"124": None, "125": None},
            "displacement": [0, 0, 0],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Number of entries does not match arguments"}

    response = client.post(
        f"models/{planet_double_arg_mercury.formula_id}/estimate/",
        json={
            "arg1": arg1,
            "arg2": arg2,
            "entries": [0] * len(arg1) * len(arg2),
            "params": {"124": 1, "125": 2},
            "displacement": [0, 0, 0],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "No parameter to estimate"}


def test_model_tablecontent_validation():
    def post(json: dict):
        return client.post(
            "models/23/fill/",
            json={
                "arg1": [1, 2, 3],
                "params": {"50": 1},
                "displacement": [0, 0, 0],
            }
            | json,
        )

    response = post({"params": {"30": 3}})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid parameters, (50,)"}

    response = post({"arg1": []})
    assert response.status_code == 400
    assert response.json() == {"detail": "Arguments cannot be empty"}

    response = post({"displacement": [1, 2]})
    assert response.status_code == 400
    assert response.json() == {"detail": "Displacement array must have 3 elements"}

    response = post({"arg2": [1, 2]})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid number of arguments"}


def test_openapi():
    response = client.get("/openapi.json")

    assert response.status_code == 200
