import requests
from typing import Any, Dict, List, Optional, Union


class BaseAPIClient:
    """Only path for api, not endpoint. For example: api/v1"""

    HOST: str = None

    def __init__(self, api_key: str = None) -> None:
        if not self.HOST:
            raise ValueError("HOST must be set.")
        self.api_key = api_key

    def _get_headers(self) -> dict[str, str]:
        """Default headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get_headers(self, headers: Optional[Dict[str, str]] = None):
        if headers is None:
            headers = {}

        default_headers = self._get_headers()
        default_headers.update(headers)
        return default_headers


class FetchAPIClient(BaseAPIClient):
    ENTITY_PATH: str
    ORDER_MAP: Dict[str, str] = {}
    FILTERS_MAP: Dict[str, str] = {}

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make a GET request to the API.
        :param endpoint: API endpoint
        :param params: Query parameters
        :param headers: Custom headers
        :return Response object
        """
        url = f"{self.HOST}/{endpoint}"
        try:
            response = requests.get(
                url=url, headers=self.get_headers(headers), params=params, **kwargs
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"Error during GET request to {url}: Detail error: {e}")

    def fetch_objects(
        self,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        orders: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Fetch an object with optional filters and parameters.
        :param entity_url: Entity specific url.
        :param headers: Additional headers
        :param params: Query params
        :param filters: Filters for fetching object
        """
        params = self.get_params(params=params, filters=filters, orders=orders)

        response = self.get(
            endpoint=self.ENTITY_PATH, params=params, headers=headers, **kwargs
        )
        try:
            return self.get_rows(response)
        except ValueError:
            raise ValueError("Failed to parse JSON from response.")

    def get_params(
        self,
        params: Optional[Dict[str, str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        orders: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        if params is None:
            params = {}
        if filters:
            params["filter"] = self.parse_filters(**filters)
        if orders:
            params["order"] = self.parse_orders(orders)
        return params

    def parse_filters(self, **filters) -> str:
        """
        This method for parsing request filters from keyword
        args(**kwargs). You need to implement the logic of
        parsing filters for request to api service. For example,
        here is filter parser implementation for api.moysklad.ru,
        where filters are query params, and symbols for filtering
        maps from FILTERS_MAP: For example:
        """
        parsed_filters = []
        for key, value in filters.items():
            parts = key.split("__")
            if len(parts) == 1:
                parsed_filters.append(f"{key}={value}")
            elif len(parts) == 2:
                field, lookup = parts
                operator = self.FILTERS_MAP.get(lookup)
                if operator is None:
                    raise ValueError(
                        f"Unsupported lookup '{lookup}' in filter key '{key}'"
                    )
                parsed_filters.append(f"{field}{operator}{value}")
            else:
                raise ValueError(
                    "Invalid filter format. Use at most one '__' in filter keys"
                )

        return ";".join(parsed_filters)

    def parse_orders(self, orders: List[str]) -> str:
        """
        This method for parsing request orders from keyword
        args(**kwargs). It generates the order query parameters

        Example:
        For input orders:
        parse_orders(weighed="desc", weight="desc", name="asc")
        it will return:
        'weighed,desc;weight,desc;name,asc'
        """
        parsed_orders = []

        for item in orders:
            field, lookup = item.split("__")
            mapped_lookup = self.ORDERS_MAP.get(lookup)
            if not mapped_lookup:
                raise ValueError(
                    f"Unsupported lookup '{lookup}' in order field '{field}'"
                )
            parsed_orders.append(f"{field},{mapped_lookup}")

        return ";".join(parsed_orders)

    def get_rows(
        self, response: requests.Response
    ) -> Union[Dict[str, Any], List[Dict[str, str]]]:
        # return response.json()["rows"] - Something like this.
        pass


class CreateModel(BaseAPIClient):
    """
    A mixin class to provide create functionality for API clients.
    Attributes:
        HOST (str): The base URL of the API.
        ENTITY_PATH (str): The specific path for the entity being created.
    Methods:
        create(data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
            Sends a POST request to create a new entity with the provided data and headers.
        post(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> requests.Response:
            Sends a POST request to the specified URL with the provided data and headers.

    """

    def create(
        self,
        data: Dict[str, Any],
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        url = f"{self.HOST}/{endpoint}"
        headers = self.get_headers(headers)
        response = self.post(url=url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def post(
        self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        response = requests.post(url=url, headers=self.get_headers(headers), json=data)
        response.raise_for_status()
        return response


class UpdateModel(BaseAPIClient):
    """
    A mixin class to provide create functionality for API clients.
    Attributes:
        HOST (str): The base URL of the API.
        ENTITY_PATH (str): The specific path for the entity being created.
    Methods:
        _update(data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
            Sends a PATCH request to update a exist entity with the provided data and headers.
        patch(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> requests.Response:
            Sends a PATCH request to the specified URL with the provided data and headers.
    """

    def update(
        self,
        data: Dict[str, Any],
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        id = kwargs.get("id", None)
        if not id:
            raise ValueError("Need 'id' for a request")
        url = f"{self.HOST}/{endpoint}/{id}"
        headers = self.get_headers(headers)
        response = self.put(url=url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def put(
        self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        response = requests.put(url=url, headers=self.get_headers(headers), json=data)
        response.raise_for_status()
        return response
