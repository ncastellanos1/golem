from src.client.base import BaseClient
import requests

class AIClient(BaseClient):
    def get_prompt_template(self, prompt_id: str, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.get(f"/ai/prompt-template/{prompt_id}", cookies=cookies, headers=headers)

    def create_prompt_override(self, prompt_key: str, payload: dict, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.put(f"/ai/prompts/{prompt_key}/override", json=payload, cookies=cookies, headers=headers)

    def list_prompt_overrides(self, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.get("/ai/prompts/overrides", cookies=cookies, headers=headers)

    def delete_prompt_override(self, prompt_key: str, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.delete(f"/ai/prompts/{prompt_key}/override", cookies=cookies, headers=headers)

    def create_base_prompt(self, payload: dict, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.post("/ai/prompts", json=payload, cookies=cookies, headers=headers)

    def update_base_prompt(self, prompt_key: str, payload: dict, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.put(f"/ai/prompts/{prompt_key}", json=payload, cookies=cookies, headers=headers)

    def list_base_prompts(self, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.get("/ai/prompts", cookies=cookies, headers=headers)

    def delete_base_prompt(self, prompt_key: str, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.delete(f"/ai/prompts/{prompt_key}", cookies=cookies, headers=headers)

    def create_feedback(self, payload: dict, cookies: dict = None, headers: dict = None) -> requests.Response:
        return self.post("/ai/feedback", json=payload, cookies=cookies, headers=headers)
