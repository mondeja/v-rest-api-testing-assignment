import os

import pytest
import requests
import jsonschema
import json
from faker import Faker

BASE_URL = "https://gorest.co.in/public/v2"
TOKEN = os.environ.get("API_TOKEN")


def pytest_configure(config):
    if not TOKEN:
        pytest.exit("API_TOKEN environment variable is not set. Set it to run tests.\n")


@pytest.fixture(scope="session")
def rest_client():
    class Client:
        def __init__(self):
            self.session = requests.Session()

        def get(self, endpoint, params=None):
            params = params or {}
            return self.session.get(f"{BASE_URL}{endpoint}", params=params)

        def post(self, endpoint, data):
            headers = {"Authorization": f"Bearer {TOKEN}"}
            return self.session.post(
                f"{BASE_URL}{endpoint}", json=data, headers=headers
            )
        
        def put(self, endpoint, data):
            headers = {"Authorization": f"Bearer {TOKEN}"}
            return self.session.put(
                f"{BASE_URL}{endpoint}", json=data, headers=headers
            )
        
        def delete(self, endpoint):
            headers = {"Authorization": f"Bearer {TOKEN}"}
            return self.session.delete(f"{BASE_URL}{endpoint}", headers=headers)

    return Client()


@pytest.fixture(scope="session", autouse=True)
def response_is_json():
    def response_is_json_(response):
        return response.headers["Content-Type"] == "application/json; charset=utf-8"

    return response_is_json_


@pytest.fixture(scope="session")
def validate_jsonschema(request):
    pytest_verbose_mode = request.config.getoption("verbose") > 0
    truncated_instance_max_length = 300

    def validate_jsonschema_(instance, schema):
        validator = jsonschema.Draft7Validator(schema)
        errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
        if errors:
            errors_list = map(lambda e: f"{list(e.path)} -> {e.message}", errors)
            errors_list_as_str = "\n".join(errors_list)
            instance_as_str = json.dumps(instance, indent=2)
            if not pytest_verbose_mode:
                instance_as_str = instance_as_str[:truncated_instance_max_length] + (
                    "...\n[TRUNCATED] (pass -v to show)\n"
                    if len(instance_as_str) > truncated_instance_max_length
                    else ""
                )
            errors_msg = (
                "Instance:\n"
                f"{instance_as_str}\n\n"
                "JSON schema validation errors:\n"
                f"{errors_list_as_str}"
                "\n------------------------------------------------\n"
            )
            pytest.fail(errors_msg, pytrace=False)

    return validate_jsonschema_


@pytest.fixture(scope="session")
def fake(request):
    faker_instance = Faker()

    FAKER_SEED = os.environ.get("FAKER_SEED")
    if FAKER_SEED:
        if not FAKER_SEED.isdigit():
            pytest.exit("FAKER_SEED environment variable must be an integer.\n")
        seed = int(FAKER_SEED)
        faker_instance.seed_instance(seed)
    return faker_instance


@pytest.fixture(scope="session")
def get_schema():
    schemas_cache = {}
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    

    def get_schema_(name):
        if name in schemas_cache:
            return schemas_cache[name]

        schema_path = os.path.join(this_dir_path, "schemas", f"{name}.json")
        with open(schema_path) as f:
            schema = json.load(f)
            schemas_cache[name] = schema
            return schema

    return get_schema_


@pytest.fixture
def create_user(rest_client, response_is_json, get_schema, fake, validate_jsonschema):
    def create_user_(email=None):
        if email is None:
            email = fake.email()
        data = {
            "name": fake.name(),
            "email": email,
            "gender": fake.random_element(["male", "female"]),
            "status": fake.random_element(["active", "inactive"]),
        }
        response = rest_client.post("/users", data=data)
        assert response.status_code == 201
        assert response_is_json(response)
        result = response.json()
        return result["id"]
    return create_user_