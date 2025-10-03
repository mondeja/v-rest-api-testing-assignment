import pytest

GENDERS = ["make", "female"]
STATUSES = ["active", "inactive"]


@pytest.mark.parametrize(
    ("data",),
    (
        pytest.param(
            {},
            id="no-fields",
        ),
        pytest.param(
            {
                "name": "<random>",
            },
            id="name",
        ),
        pytest.param(
            {
                "email": "<random>",
            },
            id="email",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "<random>",
            },
            id="name-email",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "<random>",
                "gender": "female",
            },
            id="name-email-gender",
        ),
        pytest.param(
            {
                "email": "<random>",
                "status": "inactive",
            },
            id="email-status",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "<random>",
                "gender": "male",
                "status": "inactive",
            },
            id="all",
        ),
    ),
)
def test_update_user_ok(
    data,
    create_user,
    rest_client,
    fake,
    response_is_json,
    get_schema,
    validate_jsonschema,
):
    user_id = create_user()
    data = data.copy()
    if data.get("name") == "<random>":
        data["name"] = fake.name()
    if data.get("email") == "<random>":
        data["email"] = fake.email()
    if data.get("gender") == "<random>":
        data["gender"] = fake.random_element(GENDERS)
    if data.get("status") == "<random>":
        data["status"] = fake.random_element(STATUSES)

    path = f"/users/{user_id}"
    response = rest_client.put(path, data=data)
    assert response.status_code == 200
    assert response_is_json(response)
    result = response.json()

    schema = get_schema("user")
    validate_jsonschema(result, schema)

    assert result["id"] == user_id
    if "name" in data:
        assert result["name"] == data["name"]
    if "email" in data:
        assert result["email"] == data["email"]
    if "gender" in data:
        assert result["gender"] == data["gender"]
    if "status" in data:
        assert result["status"] == data["status"]


@pytest.mark.parametrize(
    ("data", "expected_messages"),
    (
        pytest.param(
            {
                "name": "",
            },
            [
                {"field": "name", "message": "can't be blank"},
            ],
            id="empty-name",
        ),
        pytest.param(
            {
                "email": "foobar",
            },
            [
                {"field": "email", "message": "is invalid"},
            ],
            id="invalid-email",
        ),
        pytest.param(
            {
                "name": "",
                "email": "foobar",
            },
            [
                {"field": "email", "message": "is invalid"},
                {"field": "name", "message": "can't be blank"},
            ],
            id="empty-name-invalid-email",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "",
            },
            [
                {"field": "email", "message": "can't be blank"},
            ],
            id="name-empty-email",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "barbaz",
            },
            [
                {"field": "email", "message": "is invalid"},
            ],
            id="name-invalid-email",
        ),
        pytest.param(
            {
                "name": "<random>",
                "email": "<random>",
                "gender": "foobar",
            },
            [
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
def test_update_user_invalid_data(
    rest_client, create_user, data, fake, expected_messages, response_is_json
):
    data = data.copy()
    if data.get("name") == "<random>":
        data["name"] = fake.name()
    if data.get("email") == "<random>":
        data["email"] = fake.email()

    user_id = create_user()
    response = rest_client.put(f"/users/{user_id}", data=data)
    assert response.status_code == 422
    assert response_is_json(response)
    result = response.json()
    assert isinstance(result, list)

    sorted_result = sorted(result, key=lambda x: x["field"])
    sorted_expected = sorted(expected_messages, key=lambda x: x["field"])
    assert sorted_result == sorted_expected


def test_update_non_existing_user(rest_client, fake, response_is_json):
    user_id = -1
    name = fake.name()
    email = fake.email()
    gender = fake.random_element(GENDERS)
    status = fake.random_element(STATUSES)
    data = {
        "name": name,
        "email": email,
        "gender": gender,
        "status": status,
    }

    path = f"/users/{user_id}"
    response = rest_client.put(path, data=data)
    assert response.status_code == 404
    assert response_is_json(response)
    result = response.json()
    assert result == {"message": "Resource not found"}


def test_update_user_with_taken_email(rest_client, create_user, fake, response_is_json):
    email = fake.email()
    create_user(email=email)
    user_id = create_user()
    data = {
        "email": email,
    }
    path = f"/users/{user_id}"
    response = rest_client.put(path, data=data)
    assert response.status_code == 422
    assert response_is_json(response)
    result = response.json()
    assert isinstance(result, list)
    assert result == [{"field": "email", "message": "has already been taken"}]
