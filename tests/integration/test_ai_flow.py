import pytest
import uuid
from src.client.ai import AIClient
from src.client.auth import AuthClient
from src.client.transaction import TransactionClient
from tests.integration.schemas import BasePromptRequest, PromptOverrideRequest, TransactionAIPayloadRequest, FeedbackRequest


@pytest.mark.integration
class TestAIFlow:
    def test_get_ai_prompt_template(self, ai_client, auth_session):
        """
        Scenario: Getting an AI prompt template that does not exist or has no override falls back cleanly or returns 404.
        """
        res = ai_client.get_prompt_template("transaction_extraction", **auth_session)
        
        assert res.status_code == 404

    def test_prompt_override_and_isolation(self, ai_client, transaction_client, auth_session):
        """
        Scenario: Creating a prompt override isolates the behavior to the specific user session.
        """
        override_payload = PromptOverrideRequest(
            template="Eres un asistente financiero muy estricto. Siempre clasifica los gastos de comida como 'Supervivencia'."
        ).model_dump()
        res_override = ai_client.create_prompt_override("transaction_extraction", override_payload, **auth_session)
        assert res_override.status_code == 201

        tx_payload = TransactionAIPayloadRequest(
            description="Compré una pizza de 20 dolares"
        ).model_dump()
        res_tx = transaction_client.create_from_ai_description(tx_payload, **auth_session)
        assert res_tx.status_code == 201
        
        # Strict schema validation
        from tests.integration.schemas import TransactionModel
        tx_model = TransactionModel(**res_tx.json().get("data", {}))

    def test_list_and_delete_overrides(self, ai_client, auth_session):
        """
        Scenario: Listing and deleting prompt overrides correctly updates the active overrides for the user.
        """
        res_list = ai_client.list_prompt_overrides(**auth_session)
        assert res_list.status_code == 200

        override_payload = PromptOverrideRequest(template="Test template").model_dump()
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
        """
        Scenario: Administering global base prompts (Create, Update, List, Delete) works appropriately.
        """
        base_payload = BasePromptRequest(key="budget_analysis", template="Analiza esto: {{data}}").model_dump()
        res_create = ai_client.create_base_prompt(base_payload, **auth_session)
        assert res_create.status_code == 201

        update_payload = PromptOverrideRequest(template="Analiza esto en tono amable: {{data}}").model_dump()
        res_update = ai_client.update_base_prompt("budget_analysis", update_payload, **auth_session)
        assert res_update.status_code == 200

        res_list = ai_client.list_base_prompts(**auth_session)
        assert res_list.status_code == 200

        res_del = ai_client.delete_base_prompt("budget_analysis", **auth_session)
        assert res_del.status_code == 204

    def test_create_duplicate_base_prompt(self, ai_client, auth_session):
        """
        Scenario: Creating a duplicate base prompt returns a 409 Conflict.
        """
        prompt_key = f"duplicate_test_{uuid.uuid4().hex[:8]}"
        base_payload = BasePromptRequest(key=prompt_key, template="Test 1: {{data}}").model_dump()
        res_create = ai_client.create_base_prompt(base_payload, **auth_session)
        assert res_create.status_code == 201

        res_conflict = ai_client.create_base_prompt(base_payload, **auth_session)
        assert res_conflict.status_code == 409

        from src.models.response.auth import ErrorResponse
        error_data = res_conflict.json()
        ErrorResponse(**error_data)

        error_message = error_data.get("title", "") or error_data.get("message", "") or error_data.get("detail", "")
        assert "Ya existe un prompt con esta llave" in error_message

        ai_client.delete_base_prompt(prompt_key, **auth_session)


    @pytest.mark.parametrize("scenario,payload,expected_status", [
        ("Valid Feedback", FeedbackRequest(usage_id="temp", rating=4, comment="La categoría asignada fue buena.").model_dump(), 201),
        ("Invalid Rating High", {"usage_id": "temp", "rating": 6}, 400),
        ("Invalid Rating Low", {"usage_id": "temp", "rating": 0}, 400),
        ("Empty Usage ID", {"usage_id": "", "rating": 3}, 400)
    ])
    def test_submit_ai_feedback(self, ai_client, auth_session, scenario, payload, expected_status):
        """
        Scenario: Submitting AI usage feedback validates rating ranges and handles insertions cleanly.
        """
        if scenario != "Empty Usage ID":
            payload["usage_id"] = str(uuid.uuid4())
            
        res = ai_client.create_feedback(payload, **auth_session)
        
        assert res.status_code == expected_status

    def test_unauthorized_feedback(self, ai_client):
        """
        Scenario: Unauthorized feedback submission returns 401.
        """
        payload = FeedbackRequest(usage_id=str(uuid.uuid4()), rating=4).model_dump()
        res = ai_client.create_feedback(payload, cookies={})
        assert res.status_code == 401
