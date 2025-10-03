import pytest


@pytest.fixture(scope="module")
def todos_list(rest_client, response_is_json):
    response = rest_client.get("/todos")
    assert response.status_code == 200
    assert response_is_json(response)
    return response.json()


def test_get_todos_schema(todos_list, get_schema, validate_jsonschema):
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {
            "todo": get_schema("todo"),
        },
        "type": "array",
        "minItems": 1,
        "items": {"$ref": "#/definitions/todo"},
        "uniqueItems": True,
    }
    validate_jsonschema(todos_list, schema)


def test_get_todos_unique_ids(todos_list):
    ids = [post["id"] for post in todos_list]
    assert sorted(ids) == sorted(list((set(ids)))), "Post IDs are not unique"


@pytest.mark.parametrize(
    ("page", "per_page", "expected_number_of_todos"),
    (
        pytest.param(
            1,
            2,
            2,
            id="page-1-2-items",
        ),
        pytest.param(
            2,
            5,
            5,
            id="page-2-5-items",
        ),
        pytest.param(
            9999999,
            5,
            0,
            id="page-out-of-range",
        ),
    ),
)
def test_get_todos_pagination(
    rest_client,
    response_is_json,
    page,
    per_page,
    expected_number_of_todos,
):
    response = rest_client.get("/todos", params={"page": page, "per_page": per_page})
    assert response.status_code == 200
    assert response_is_json(response)
    headers = response.headers
    assert headers.get("X-Pagination-Page") == str(page)
    assert headers.get("X-Pagination-Limit") == str(per_page)

    todos = response.json()
    assert len(todos) == expected_number_of_todos
