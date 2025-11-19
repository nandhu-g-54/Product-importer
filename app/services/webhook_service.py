import requests

def test_webhook(url: str):
    try:
        resp = requests.post(url, json={"test": "data"}, timeout=5)
        return {"status_code": resp.status_code, "response": resp.text}
    except Exception as e:
        return {"error": str(e)}
