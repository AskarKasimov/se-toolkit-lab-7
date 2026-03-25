import httpx
from typing import Any, Dict, List


class LMSClient:
    """A client for interacting with the LMS API."""

    def __init__(self, base_url: str, api_key: str):
        """
        Initializes the LMS client.

        Args:
            base_url: The base URL of the LMS API.
            api_key: The API key for authentication.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def get_health(self) -> str:
        """
        Checks the health of the LMS API.

        Returns:
            A string indicating the health status.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/items/", headers=self.headers
                )
                response.raise_for_status()
                return "Health is ok"
            except httpx.ConnectError as e:
                return f"Backend error: connection refused ({e.request.url}). Check that the services are running."
            except httpx.HTTPStatusError as e:
                return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
            except Exception as e:
                return f"Backend error: {e}"

    async def get_labs(self) -> List[Dict[str, Any]]:
        """
        Fetches the list of available labs.

        Returns:
            A list of lab dictionaries.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/items/", headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_scores(self, lab_id: str) -> List[Dict[str, Any]]:
        """
        Fetches the pass rates for a specific lab.

        Args:
            lab_id: The ID of the lab.

        Returns:
            A list of dictionaries containing pass rate information.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/analytics/pass-rates?lab={lab_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
