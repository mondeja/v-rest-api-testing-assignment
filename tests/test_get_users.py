import pytest


@pytest.fixture(scope="module")
def users_list(rest_client, response_is_json):
    response = rest_client.get("/users")
    assert response.status_code == 200
    assert response_is_json(response)
    return response.json()


def test_get_users_schema(users_list, get_schema, validate_jsonschema):
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {
            "user": get_schema("user"),
        },
        "type": "array",
        "minItems": 1,
        "items": {"$ref": "#/definitions/user"},
    }
    validate_jsonschema(users_list, schema)


def test_get_users_unique_ids(users_list):
    ids = [user["id"] for user in users_list]
    assert sorted(ids) == sorted(list((set(ids)))), "User IDs are not unique"


@pytest.mark.parametrize(
    ("page", "per_page", "expected_number_of_users"),
    (
        pytest.param(
            1,
            2,
            2,
            id="page-1",
        ),
        pytest.param(
            2,
            5,
            5,
            id="page-2",
        ),
        pytest.param(
            9999999,
            5,
            0,
            id="page-out-of-range",
        ),
    ),
)
def test_get_users_pagination(
    rest_client,
    page,
    per_page,
    expected_number_of_users,
    response_is_json,
):
    response = rest_client.get("/users", params={"page": page, "per_page": per_page})
    assert response.status_code == 200
    assert response_is_json(response)
    headers = response.headers
    assert headers.get("X-Pagination-Page") == str(page)
    assert headers.get("X-Pagination-Limit") == str(per_page)

    users = response.json()
    assert len(users) == expected_number_of_users
