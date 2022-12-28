from fastapi.testclient import TestClient

from app.app import SupportedModels, app

client = TestClient(app)


def test_get_models():
    response = client.get("/models")
    assert response.status_code == 200

    data = response.json()['variants']
    assert len(data) == len(
        SupportedModels), 'Returned less models than supported'

    ids = [d['id'] for d in data]
    assert len(set(ids)) == len(ids), 'IDs are not unique'


def test_train_session():
    response = client.post("/training/session")
    assert response.status_code == 200
