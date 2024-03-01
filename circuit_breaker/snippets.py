
import http
from fastapi import requests
from breaker import circuit_breaker


@circuit_breaker()
def make_request(url):
    try:
        response = requests.get(url, timeout=0.3)
        if response.status_code == http.HTTPStatus.OK:
            print(f"Call to {url} succeed with status code = {response.status_code}")
            return response
        if 500 <= response.status_code < 600:
            print(f"Call to {url} failed with status code = {response.status_code}")
            raise Exception("Server Issue")
    except Exception:
        print(f"Call to {url} failed")
        raise