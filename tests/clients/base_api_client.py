import json
import requests
import allure


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

    def _attach_to_allure(self, response: requests.Response):
        """Attach request and response details to the Allure report."""
        request = response.request

        # Mask the API key in the URL for the report
        url_display = response.url.replace(self.api_key, "***")

        request_body = None
        if request.body:
            try:
                request_body = json.dumps(json.loads(request.body), indent=2)
            except (ValueError, TypeError):
                request_body = str(request.body)

        try:
            response_body = json.dumps(response.json(), indent=2)
        except ValueError:
            response_body = response.text

        allure.attach(
            f"{request.method}  {url_display}\nStatus: {response.status_code}",
            name="Request",
            attachment_type=allure.attachment_type.TEXT,
        )
        if request_body:
            allure.attach(
                request_body,
                name="Request Body",
                attachment_type=allure.attachment_type.JSON,
            )
        allure.attach(
            response_body,
            name="Response Body",
            attachment_type=allure.attachment_type.JSON,
        )

    def raw_get(self, endpoint: str, params: dict = None):
        """GET without raising on error — use in negative tests to inspect error response body."""
        url = f"{self.base_url}{endpoint}"
        params = self._add_api_key(params)
        response = requests.get(
            url, headers=self.headers, params=params, timeout=self.timeout
        )
        self._attach_to_allure(response)
        return response

    def raw_post(self, endpoint: str, data: dict = None, params: dict = None):
        """POST without raising on error — use in negative tests to inspect error response body."""
        url = f"{self.base_url}{endpoint}"
        params = self._add_api_key(params)
        response = requests.post(
            url, headers=self.headers, json=data, params=params, timeout=self.timeout
        )
        self._attach_to_allure(response)
        return response

    def raw_delete(self, endpoint: str, params: dict = None):
        """DELETE without raising on error — use in negative tests to inspect error response body."""
        url = f"{self.base_url}{endpoint}"
        params = self._add_api_key(params)
        response = requests.delete(
            url, headers=self.headers, params=params, timeout=self.timeout
        )
        self._attach_to_allure(response)
        return response

    def raw_put(self, endpoint: str, data: dict = None, params: dict = None):
        """PUT without raising on error — use in negative tests to inspect error response body."""
        url = f"{self.base_url}{endpoint}"
        params = self._add_api_key(params)
        response = requests.put(
            url, headers=self.headers, json=data, params=params, timeout=self.timeout
        )
        self._attach_to_allure(response)
        return response

    def _validate_response(self, response: requests.Response):
        self._attach_to_allure(response)
        if response.ok:
            return response
        raise Exception(f"API request failed: {response.status_code} - {response.text}")
