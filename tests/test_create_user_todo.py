import pytest
from datetime import timezone, timedelta

STATUSES = ["pending", "completed"]


@pytest.mark.parametrize(
    "data",
    (
        pytest.param(
            {
                "title": "<random>",
                "due_on": "<random>",
                "status": "<random>",
            },
            id="all-fields",
        ),
        pytest.param(
            {
                "title": "<random>",
                "status": "<random>",
            },
            id="missing-due_on",
        ),
    ),
)
def test_create_user_todo_ok(
    create_user,
    rest_client,
    data,
    fake,
    response_is_json,
    get_schema,
    validate_jsonschema,
):
    user_id = create_user()
    data = data.copy()
    if data.get("title") == "<random>":
        data["title"] = fake.sentence(nb_words=6)
    if data.get("due_on") == "<random>":
        tz = timezone(timedelta(hours=5, minutes=30))
        data["due_on"] = fake.date_time(tzinfo=tz).isoformat(timespec="milliseconds")
    if data.get("status") == "<random>":
        data["status"] = fake.random_element(STATUSES)

    path = f"/users/{user_id}/todos"
    response = rest_client.post(path, data=data)
    assert response.status_code == 201
    assert response_is_json(response)
    result = response.json()

    schema = get_schema("todo")
    validate_jsonschema(result, schema)

    assert result["user_id"] == user_id
    assert result["title"] == data.get("title")
    assert result["due_on"] == data.get("due_on")
    assert result["status"] == data.get("status")

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
                {
                    "field": "status",
                    "message": "can't be blank, can be pending or completed",
                },
            ],
            id="no-fields",
        ),
        pytest.param(
            {
                "title": "",
                "status": "",
            },
            [
                {"field": "title", "message": "can't be blank"},
                {
                    "field": "status",
                    "message": "can't be blank, can be pending or completed",
                },
            ],
            id="empty-title-status",
        ),
        pytest.param(
            {
                "title": "<random>",
                "status": "invalid-status",
            },
            [
                {
                    "field": "status",
                    "message": "can't be blank, can be pending or completed",
                },
            ],
            id="invalid-status",
        ),
        pytest.param(
            {
                "title": "",
                "status": "<random>",
            },
            [
                {"field": "title", "message": "can't be blank"},
            ],
            id="empty-title",
        ),
    ),
)
def test_create_user_todo_invalid_data(
    rest_client, create_user, data, expected_messages, fake, response_is_json
):
    data = data.copy()
    if data.get("title") == "<random>":
        data["title"] = fake.sentence(nb_words=6)
    if data.get("status") == "<random>":
        data["status"] = fake.random_element(STATUSES)
    if data.get("due_on") == "<random>":
        tz = timezone(timedelta(hours=5, minutes=30))
        data["due_on"] = fake.date_time(tzinfo=tz).isoformat(timespec="milliseconds")

    user_id = create_user()
    path = f"/users/{user_id}/todos"
    response = rest_client.post(path, data=data)
    assert response.status_code == 422
    assert response_is_json(response)
    result = response.json()
    assert isinstance(result, list)

    sorted_result = sorted(result, key=lambda x: x["field"])
    sorted_expected = sorted(expected_messages, key=lambda x: x["field"])
    assert sorted_result == sorted_expected


def test_create_user_todo_non_existing_user(rest_client, fake, response_is_json):
    user_id = -1  # Assuming this user ID does not exist
    title = fake.sentence(nb_words=6)
    status = fake.random_element(STATUSES)
    data = {
        "user_id": user_id,
        "title": title,
        "status": status,
    }

    path = f"/users/{user_id}/todos"
    response = rest_client.post(path, data=data)
    assert response.status_code == 422
    assert response_is_json(response)
    result = response.json()
    assert isinstance(result, list)
    assert result == [{"field": "user", "message": "must exist"}]
