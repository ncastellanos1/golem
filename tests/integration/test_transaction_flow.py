import pytest
from src.client.transaction import TransactionClient
from src.client.auth import AuthClient

@pytest.mark.integration
class TestTransactionFlow:
    def test_create_transaction_existing_category(self, transaction_client, ai_client, auth_session):
        ai_client.create_base_prompt({"key": "transaction_extraction", "template": "Extract tx data from: {{description}}"}, **auth_session)
        ai_client.create_base_prompt({"key": "category_determination", "template": "Determine category for: {{title}}"}, **auth_session)
        
        payload = {
            "description": "Compré dos hamburguesas y un refresco por 15 dolares en McDonalds"
        }
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        
        assert res.status_code == 201
        from tests.integration.schemas import TransactionModel
        tx_model = TransactionModel(**res.json().get("data", {}))

    def test_create_transaction_new_category_ai(self, transaction_client, ai_client, auth_session):
        ai_client.create_base_prompt({"key": "transaction_extraction", "template": "Extract tx data from: {{description}}"}, **auth_session)
        ai_client.create_base_prompt({"key": "category_determination", "template": "Determine category for: {{title}}"}, **auth_session)

        payload = {
            "description": "Paid $50 for a completely new unknown subscription service"
        }
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        assert res.status_code == 201

        from tests.integration.schemas import TransactionModel
        tx_model = TransactionModel(**res.json().get("data", {}))

    @pytest.mark.parametrize("scenario,payload,expected", [
        ("AI extraction failure", {"description": "asdf123 xyz"}, 201),
        ("missing extraction prompt", {}, 400)
    ])
    def test_create_transaction_failures(self, transaction_client, auth_session, scenario, payload, expected):
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        
        assert res.status_code == expected

