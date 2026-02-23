import pytest
from src.client.transaction import TransactionClient
from src.client.auth import AuthClient
from tests.integration.schemas import BasePromptRequest, TransactionAIPayloadRequest

@pytest.mark.integration
class TestTransactionFlow:
    def test_create_transaction_existing_category(self, transaction_client, ai_client, auth_session):
        """
        Scenario: Create transaction from AI description using an existing category
        """
        ai_client.create_base_prompt(BasePromptRequest(key="transaction_extraction", template="Extract tx data from: {{description}}").model_dump(), **auth_session)
        ai_client.create_base_prompt(BasePromptRequest(key="category_determination", template="Determine category for: {{title}}").model_dump(), **auth_session)
        
        payload = TransactionAIPayloadRequest(
            description="Compré dos hamburguesas y un refresco por 15 dolares en McDonalds"
        ).model_dump()
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        
        assert res.status_code == 201
        from tests.integration.schemas import TransactionModel
        tx_model = TransactionModel(**res.json().get("data", {}))

    def test_create_transaction_new_category_ai(self, transaction_client, ai_client, auth_session):
        """
        Scenario: Create transaction from AI description requiring a new auto-generated category
        """
        ai_client.create_base_prompt(BasePromptRequest(key="transaction_extraction", template="Extract tx data from: {{description}}").model_dump(), **auth_session)
        ai_client.create_base_prompt(BasePromptRequest(key="category_determination", template="Determine category for: {{title}}").model_dump(), **auth_session)

        payload = TransactionAIPayloadRequest(
            description="Paid $50 for a completely new unknown subscription service"
        ).model_dump()
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        assert res.status_code == 201

        from tests.integration.schemas import TransactionModel
        tx_model = TransactionModel(**res.json().get("data", {}))

    @pytest.mark.parametrize("scenario,payload,expected", [
        ("AI extraction failure", TransactionAIPayloadRequest(description="asdf123 xyz").model_dump(), 201),
        ("missing extraction prompt", {}, 400)
    ])
    def test_create_transaction_failures(self, transaction_client, auth_session, scenario, payload, expected):
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        
        assert res.status_code == expected

