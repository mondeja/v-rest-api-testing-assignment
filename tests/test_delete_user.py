def test_delete_user_ok(
    rest_client, create_user, fake, response_is_json, get_schema, validate_jsonschema
):
    user_id = create_user()
    path = f"/users/{user_id}"
    response = rest_client.delete(path)
    assert response.status_code == 204
    headers = response.headers
    assert "Content-Type" not in headers
    assert response.text == ""


def test_delete_non_existing_user(rest_client, fake, response_is_json):
    user_id = -1
    path = f"/users/{user_id}"
    response = rest_client.delete(path)
    assert response.status_code == 404
    assert response_is_json(response)
    result = response.json()
    assert result == {'message': 'Resource not found'}
