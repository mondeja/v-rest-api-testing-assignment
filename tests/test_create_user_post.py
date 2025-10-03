import pytest


def test_create_user_post_ok(
    create_user, rest_client, fake, response_is_json, get_schema, validate_jsonschema
):
    user_id = create_user()
    title = fake.sentence(nb_words=6)
    body = fake.text(max_nb_chars=200)
    data = {
        "user_id": user_id,
        "title": title,
        "body": body,
    }

    path = f"/users/{user_id}/posts"
    response = rest_client.post(path, data=data)
    assert response.status_code == 201
    assert response_is_json(response)
    result = response.json()

    schema = get_schema("post")
    validate_jsonschema(result, schema)

    assert result["user_id"] == user_id
    assert result["title"] == title
    assert result["body"] == body

    assert "id" in result
    assert isinstance(result["id"], int)
    assert result["id"] > 0


@pytest.mark.parametrize(
    ("data", "expected_messages"),
    (
        pytest.param(
            {},
            [
                {"field": "title", "message": "can't be blank"},
                {"field": "body", "message": "can't be blank"},
            ],
            id="no-fields",
        ),
        pytest.param(
            {
                "title": "<random>",
            },
            [
                {"field": "body", "message": "can't be blank"},
            ],
            id="title",
        ),
        pytest.param(
            {
                "title": "",
            },
            [
                {"field": "title", "message": "can't be blank"},
                {"field": "body", "message": "can't be blank"},
            ],
            id="empty-title",
        ),
        pytest.param(
            {
                "body": "<random>",
            },
            [
                {"field": "title", "message": "can't be blank"},
            ],
            id="body",
        ),
        pytest.param(
            {
                "title": "<random>",
            },
            [
                {"field": "body", "message": "can't be blank"},
            ],
            id="empty-body",
        ),
    ),
)
def test_create_user_post_invalid_data(
    rest_client, create_user, data, expected_messages, fake, response_is_json
):
    data = data.copy()
    if data.get("title") == "<random>":
        data["title"] = fake.sentence(nb_words=6)
    if data.get("body") == "<random>":
        data["body"] = fake.text(max_nb_chars=200)

    user_id = create_user()
    path = f"/users/{user_id}/posts"
    response = rest_client.post(path, data=data)
    assert response.status_code == 422
    assert response_is_json(response)
    result = response.json()
    assert isinstance(result, list)

    sorted_result = sorted(result, key=lambda x: x["field"])
    sorted_expected = sorted(expected_messages, key=lambda x: x["field"])
    assert sorted_result == sorted_expected


def test_create_user_post_non_existing_user(rest_client, fake, response_is_json):
    user_id = -1  # Assuming this user ID does not exist
    title = fake.sentence(nb_words=6)
    body = fake.text(max_nb_chars=200)
    data = {
        "user_id": user_id,
        "title": title,
        "body": body,
    }

    path = f"/users/{user_id}/posts"
    response = rest_client.post(path, data=data)
    assert response.status_code == 422
    assert response_is_json(response)
    result = response.json()
    assert isinstance(result, list)
    assert result == [{"field": "user", "message": "must exist"}]
