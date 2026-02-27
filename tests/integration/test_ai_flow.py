import pytest
import uuid
from http import HTTPStatus
from src.client.ai import AIClient
from src.client.auth import AuthClient
from src.client.transaction import TransactionClient
from tests.integration.schemas import (
    BasePromptRequest, PromptOverrideRequest, TransactionAIPayloadRequest, 
    FeedbackRequest, TransactionResponseModel, ListPromptOverridesResponse
)
from src.models.response.auth import ErrorResponse

PROMPT_KEY_TX_EXTRACTION = "transaction_extraction"
PROMPT_KEY_BUDGET_ANALYSIS = "budget_analysis"


@pytest.mark.integration
class TestAIFlow:
    def test_get_ai_prompt_template(self, ai_client, auth_session):
        """
        Scenario: Getting an AI prompt template that does not exist or has no override falls back cleanly or returns 404.
        """
        res = ai_client.get_prompt_template(PROMPT_KEY_TX_EXTRACTION, **auth_session)
        
        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_prompt_override_and_isolation(self, ai_client, transaction_client, auth_session):
        """
        Scenario: Creating a prompt override isolates the behavior to the specific user session.
        """
        override_payload = PromptOverrideRequest(
            template="Eres un asistente financiero muy estricto. Siempre clasifica los gastos de comida como 'Supervivencia'."
        ).model_dump()
        res_override = ai_client.create_prompt_override(PROMPT_KEY_TX_EXTRACTION, override_payload, **auth_session)
        assert res_override.status_code == HTTPStatus.CREATED

        tx_payload = TransactionAIPayloadRequest(
            description="Compré una pizza de 20 dolares"
        ).model_dump()
        res_tx = transaction_client.create_from_ai_description(tx_payload, **auth_session)
        assert res_tx.status_code == HTTPStatus.CREATED
        
        # Strict schema validation
        tx_resp = TransactionResponseModel(**res_tx.json())
        tx_model = tx_resp.data

    def test_list_and_delete_overrides(self, ai_client, auth_session):
        """
        Scenario: Listing and deleting prompt overrides correctly updates the active overrides for the user.
        """
        res_list = ai_client.list_prompt_overrides(**auth_session)
        assert res_list.status_code == HTTPStatus.OK

        override_payload = PromptOverrideRequest(template="Test template").model_dump()
        ai_client.create_prompt_override(PROMPT_KEY_TX_EXTRACTION, override_payload, **auth_session)

        res_del = ai_client.delete_prompt_override(PROMPT_KEY_TX_EXTRACTION, **auth_session)
        assert res_del.status_code == HTTPStatus.NO_CONTENT

        res_list2 = ai_client.list_prompt_overrides(**auth_session)
        assert res_list2.status_code == HTTPStatus.OK
        
        overrides_resp = ListPromptOverridesResponse(**res_list2.json())
        overrides_after = overrides_resp.data or []
        assert not any(override.prompt_key == PROMPT_KEY_TX_EXTRACTION for override in overrides_after)

        res_del2 = ai_client.delete_prompt_override(PROMPT_KEY_TX_EXTRACTION, **auth_session)
        assert res_del2.status_code == HTTPStatus.NOT_FOUND

    def test_global_prompt_administration(self, ai_client, auth_session):
        """
        Scenario: Administering global base prompts (Create, Update, List, Delete) works appropriately.
        """
        base_payload = BasePromptRequest(key=PROMPT_KEY_BUDGET_ANALYSIS, template="Analiza esto: {{data}}").model_dump()
        res_create = ai_client.create_base_prompt(base_payload, **auth_session)
        assert res_create.status_code == HTTPStatus.CREATED

        update_payload = PromptOverrideRequest(template="Analiza esto en tono amable: {{data}}").model_dump()
        res_update = ai_client.update_base_prompt(PROMPT_KEY_BUDGET_ANALYSIS, update_payload, **auth_session)
        assert res_update.status_code == HTTPStatus.OK

        res_list = ai_client.list_base_prompts(**auth_session)
        assert res_list.status_code == HTTPStatus.OK

        res_del = ai_client.delete_base_prompt(PROMPT_KEY_BUDGET_ANALYSIS, **auth_session)
        assert res_del.status_code == HTTPStatus.NO_CONTENT

    def test_create_duplicate_base_prompt(self, ai_client, auth_session):
        """
        Scenario: Creating a duplicate base prompt returns a 409 Conflict.
        """
        prompt_key = f"duplicate_test_{uuid.uuid4().hex[:8]}"
        base_payload = BasePromptRequest(key=prompt_key, template="Test 1: {{data}}").model_dump()
        res_create = ai_client.create_base_prompt(base_payload, **auth_session)
        assert res_create.status_code == HTTPStatus.CREATED

        res_conflict = ai_client.create_base_prompt(base_payload, **auth_session)
        assert res_conflict.status_code == HTTPStatus.CONFLICT

        error_resp = ErrorResponse(**res_conflict.json())

        error_message = error_resp.title or error_resp.message or error_resp.detail or ""
        assert "Ya existe un prompt con esta llave" in error_message

        ai_client.delete_base_prompt(prompt_key, **auth_session)


    @pytest.mark.parametrize("scenario,payload,expected_status", [
        ("Valid Feedback", FeedbackRequest(usage_id="temp", rating=4, comment="La categoría asignada fue buena.").model_dump(), HTTPStatus.CREATED),
        ("Invalid Rating High", {"usage_id": "temp", "rating": 6}, HTTPStatus.BAD_REQUEST),
        ("Invalid Rating Low", {"usage_id": "temp", "rating": 0}, HTTPStatus.BAD_REQUEST),
        ("Empty Usage ID", {"usage_id": "", "rating": 3}, HTTPStatus.BAD_REQUEST)
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
        assert res.status_code == HTTPStatus.UNAUTHORIZED
