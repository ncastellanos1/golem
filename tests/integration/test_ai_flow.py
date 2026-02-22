import pytest
import uuid
from src.client.ai import AIClient
from src.client.auth import AuthClient
from src.client.transaction import TransactionClient


@pytest.mark.integration
class TestAIFlow:
    def test_get_ai_prompt_template(self, ai_client, auth_session):
        res = ai_client.get_prompt_template("transaction_extraction", **auth_session)
        
        assert res.status_code == 404

    def test_prompt_override_and_isolation(self, ai_client, transaction_client, auth_session):
        override_payload = {
            "template": "Eres un asistente financiero muy estricto. Siempre clasifica los gastos de comida como 'Supervivencia'."
        }
        res_override = ai_client.create_prompt_override("transaction_extraction", override_payload, **auth_session)
        assert res_override.status_code == 201

        tx_payload = {
            "description": "Compré una pizza de 20 dolares"
        }
        res_tx = transaction_client.create_from_ai_description(tx_payload, **auth_session)
        assert res_tx.status_code == 201
        
        # Strict schema validation
        from tests.integration.schemas import TransactionModel
        tx_model = TransactionModel(**res_tx.json().get("data", {}))

    def test_list_and_delete_overrides(self, ai_client, auth_session):
        res_list = ai_client.list_prompt_overrides(**auth_session)
        assert res_list.status_code == 200

        override_payload = {"template": "Test template"}
        ai_client.create_prompt_override("transaction_extraction", override_payload, **auth_session)

        res_del = ai_client.delete_prompt_override("transaction_extraction", **auth_session)
        assert res_del.status_code == 204

        res_list2 = ai_client.list_prompt_overrides(**auth_session)
        assert res_list2.status_code == 200
        overrides_after = res_list2.json().get("data") or []
        assert not any(o.get("prompt_key") == "transaction_extraction" for o in overrides_after)

        res_del2 = ai_client.delete_prompt_override("transaction_extraction", **auth_session)
        assert res_del2.status_code == 404

    def test_global_prompt_administration(self, ai_client, auth_session):
        base_payload = {"key": "budget_analysis", "template": "Analiza esto: {{data}}"}
        res_create = ai_client.create_base_prompt(base_payload, **auth_session)
        assert res_create.status_code == 201

        update_payload = {"template": "Analiza esto en tono amable: {{data}}"}
        res_update = ai_client.update_base_prompt("budget_analysis", update_payload, **auth_session)
        assert res_update.status_code == 200

        res_list = ai_client.list_base_prompts(**auth_session)
        assert res_list.status_code == 200

        res_del = ai_client.delete_base_prompt("budget_analysis", **auth_session)
        assert res_del.status_code == 204

    @pytest.mark.parametrize("scenario,payload,expected_status", [
        ("Valid Feedback", {"rating": 4, "comment": "La categoría asignada fue buena."}, 201),
        ("Invalid Rating High", {"rating": 6}, 400),
        ("Invalid Rating Low", {"rating": 0}, 400),
        ("Empty Usage ID", {"usage_id": "", "rating": 3}, 400)
    ])
    def test_submit_ai_feedback(self, ai_client, auth_session, scenario, payload, expected_status):
        if "usage_id" not in payload and scenario != "Empty Usage ID":
            payload["usage_id"] = str(uuid.uuid4())
            
        res = ai_client.create_feedback(payload, **auth_session)
        
        assert res.status_code == expected_status

    def test_unauthorized_feedback(self, ai_client):
        payload = {"usage_id": str(uuid.uuid4()), "rating": 4}
        res = ai_client.create_feedback(payload, cookies={})
        assert res.status_code == 401
