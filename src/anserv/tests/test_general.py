from fastapi.testclient import TestClient


def test_root(api_client: TestClient) -> None:
    with api_client as client:
        response = client.get('/')

    assert response.status_code == 200


def test_swagger(api_client: TestClient) -> None:
    with api_client as client:
        response = client.get('/openapi.json')

    assert response.status_code == 200
