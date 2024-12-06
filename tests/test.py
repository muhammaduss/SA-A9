import requests
import json


def test_make_request():
    for _ in range(100):
        url = "http://127.0.0.1:8000/recieve/"
        query = json.dumps({"user_alias": "student", "message": "hello"})
        response = requests.post(url, query)

    assert response.status_code == 200
