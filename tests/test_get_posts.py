import pytest


@pytest.fixture(scope="module")
def posts_list(rest_client, response_is_json):
    response = rest_client.get("/posts")
    assert response.status_code == 200
    assert response_is_json(response)
    return response.json()


def test_get_posts_schema(posts_list, get_schema, validate_jsonschema):
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {
            "post": get_schema("post"),
        },
        "type": "array",
        "minItems": 1,
        "items": {"$ref": "#/definitions/post"},
    }
    validate_jsonschema(posts_list, schema)


def test_get_posts_unique_ids(posts_list):
    ids = [post["id"] for post in posts_list]
    assert sorted(ids) == sorted(list((set(ids)))), "Post IDs are not unique"


@pytest.mark.parametrize(
    ("page", "per_page", "expected_number_of_posts"),
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
def test_get_posts_pagination(
    rest_client,
    page,
    per_page,
    expected_number_of_posts,
    response_is_json,
):
    response = rest_client.get("/posts", params={"page": page, "per_page": per_page})
    assert response.status_code == 200
    assert response_is_json(response)
    headers = response.headers
    assert headers.get("X-Pagination-Page") == str(page)
    assert headers.get("X-Pagination-Limit") == str(per_page)

    posts = response.json()
    assert len(posts) == expected_number_of_posts

    
