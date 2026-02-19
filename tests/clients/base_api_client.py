import requests


class BaseApiClient:
    """
    Base API Client to handle all HTTP requests.
    Automatically sets Bearer token, API key, base URL, and timeout.
    """

    def __init__(
        self,
        base_url: str,
        bearer_token: str,
        api_key: str,
        timeout: int = 30,
        default_location: str = "Delhi",
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self.default_location = default_location

        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _add_api_key(self, params: dict | None):
        """Ensure API key is added to query params"""
        params = params or {}
        params["apikey"] = self.api_key
        params["location"] = self.default_location
        return params

    def get(self, endpoint: str, params: dict = None):
        url = f"{self.base_url}{endpoint}"
        params = self._add_api_key(params)

        response = requests.get(
            url, headers=self.headers, params=params, timeout=self.timeout
        )
        return self._validate_response(response)

    def post(self, endpoint: str, data: dict = None, params: dict = None):
        url = f"{self.base_url}{endpoint}"
        params = self._add_api_key(params)

        response = requests.post(
            url, headers=self.headers, json=data, params=params, timeout=self.timeout
        )
        return self._validate_response(response)

    def put(self, endpoint: str, data: dict = None, params: dict = None):
        url = f"{self.base_url}{endpoint}"
        params = self._add_api_key(params)

        response = requests.put(
            url, headers=self.headers, json=data, params=params, timeout=self.timeout
        )
        return self._validate_response(response)

    def delete(self, endpoint: str, params: dict = None):
        url = f"{self.base_url}{endpoint}"
        params = self._add_api_key(params)

        response = requests.delete(
            url, headers=self.headers, params=params, timeout=self.timeout
        )
        return self._validate_response(response)

    def _validate_response(self, response: requests.Response):
        if response.ok:
            try:
                return response
            except ValueError:
                return response.text
        raise Exception(f"API request failed: {response.status_code} - {response.text}")
