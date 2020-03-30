import os
import sys
import json
from starlette.testclient import TestClient
import pytest

from fastapi_main import app

client = TestClient(app)


@pytest.fixture
def json_data():
    with open('helpers/predict_data_example.json', 'r') as json_file:
        json_data_example = json.load(json_file)
    return json_data_example


def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"msg": "OK"}


def test_predictone(json_data):
    response = client.post(
        "/predictone",
        json=json_data,
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response['price'] > json_response['prediction']*0.5
    assert json_response['price'] < json_response['prediction']*1.5


def test_predict(json_data):
    response = client.post(
        "/predict",
        json={"data": [json_data]},
    )
    assert response.status_code == 200
    json_response = response.json()['data'][0]
    assert json_response['price'] > json_response['prediction']*0.5
    assert json_response['price'] < json_response['prediction']*1.5
