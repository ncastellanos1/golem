from src.client.base import BaseClient
import requests

class TransactionClient(BaseClient):
    def create_from_ai_description(self, payload: dict, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.post("/transactions/ai", json=payload, cookies=cookies, headers=headers)
