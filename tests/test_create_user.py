import pytest


def test_create_user_ok(
    rest_client, response_is_json, get_schema, fake, validate_jsonschema
):
    name = fake.name()
    email = fake.email()
    gender = fake.random_element(["male", "female"])
    status = fake.random_element(["active", "inactive"])
    data = {
        "name": name,
        "email": email,
        "gender": gender,
        "status": status,
    }

    response = rest_client.post("/users", data=data)
    assert response.status_code == 201
    assert response_is_json(response)
    result = response.json()

    schema = get_schema("user")
    validate_jsonschema(result, schema)

    assert result["name"] == name
    assert result["email"] == email
    assert result["gender"] == gender
    assert result["status"] == status

    assert "id" in result
    assert isinstance(result["id"], int)
    assert result["id"] > 0


@pytest.mark.parametrize(
    ("data", "expected_messages"),
    (
        pytest.param(
            {},
            [
                {"field": "name", "message": "can't be blank"},
                {"field": "email", "message": "can't be blank"},
                {
                    "field": "gender",
                    "message": "can't be blank, can be male of female",
                },
                {"field": "status", "message": "can't be blank"},
            ],
            id="no-fields",
        ),
        pytest.param(
            {
                "name": "<random>",
            },
            [
                {"field": "email", "message": "can't be blank"},
                {
                    "field": "gender",
                    "message": "can't be blank, can be male of female",
                },
                {"field": "status", "message": "can't be blank"},
            ],
            id="name",
        ),
        pytest.param(
            {
                "name": "",
            },
            [
                {"field": "name", "message": "can't be blank"},
                {"field": "email", "message": "can't be blank"},
                {
                    "field": "gender",
                    "message": "can't be blank, can be male of female",
                },
                {"field": "status", "message": "can't be blank"},
            ],
            id="empty-name",
        ),
        pytest.param(
            {
                "email": "<random>",
            },
            [
                {"field": "name", "message": "can't be blank"},
                {
                    "field": "gender",
                    "message": "can't be blank, can be male of female",
                },
                {"field": "status", "message": "can't be blank"},
            ],
            id="email",
        ),
        pytest.param(
            {
                "email": "foobar",
            },
            [
                {"field": "email", "message": "is invalid"},
                {"field": "name", "message": "can't be blank"},
                {
                    "field": "gender",
                    "message": "can't be blank, can be male of female",
                },
                {"field": "status", "message": "can't be blank"},
            ],
            id="invalid-email",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "<random>",
            },
            [
                {
                    "field": "gender",
                    "message": "can't be blank, can be male of female",
                },
                {"field": "status", "message": "can't be blank"},
            ],
            id="name-email",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "",
            },
            [
                {"field": "email", "message": "can't be blank"},
                {
                    "field": "gender",
                    "message": "can't be blank, can be male of female",
                },
                {"field": "status", "message": "can't be blank"},
            ],
            id="name-empty-email",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "<random>",
                "gender": "female",
            },
            [{"field": "status", "message": "can't be blank"}],
            id="name-email-gender",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "<random>",
                "gender": "foobar",
            },
            [
                {"field": "status", "message": "can't be blank"},
                {
                    "field": "gender",
                    "message": "can't be blank, can be male of female",
                },
            ],
            id="invalid-gender",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "<random>",
                "gender": "male",
                "status": "foobar",
            },
            [
                {
                    "field": "status",
                    "message": "can't be blank",
                },
            ],
            id="invalid-status",
        ),
    ),
)
def test_create_user_invalid_data(
    rest_client, data, expected_messages, fake, response_is_json
):
    data = data.copy()
    if data.get("name") == "<random>":
        data["name"] = fake.name()
    if data.get("email") == "<random>":
        data["email"] = fake.email()

    response = rest_client.post("/users", data=data)
    assert response.status_code == 422
    assert response_is_json(response)
    result = response.json()
    assert isinstance(result, list)

    sorted_result = sorted(result, key=lambda x: x["field"])
    sorted_expected = sorted(expected_messages, key=lambda x: x["field"])
    assert sorted_result == sorted_expected
