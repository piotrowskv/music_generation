from fastapi.testclient import TestClient

from .app import SupportedModels, app

client = TestClient(app)


def test_read_main():
    response = client.get("/models")
    assert response.status_code == 200

    data = response.json()['variants']
    assert len(data) == len(
        SupportedModels), 'Returned less models than supported'

    ids = [d['id'] for d in data]
    assert len(set(ids)) == len(ids), 'IDs are not unique'
