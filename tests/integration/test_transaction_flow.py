import pytest
from http import HTTPStatus
from src.client.transaction import TransactionClient
from src.client.auth import AuthClient
from tests.integration.schemas import BasePromptRequest, TransactionAIPayloadRequest, TransactionResponseModel

PROMPT_KEY_TX_EXTRACTION = "transaction_extraction"
PROMPT_KEY_CAT_DETERMINATION = "category_determination"
PROMPT_KEY_CAT_IMAGE_GEN = "category_image_generation"

GOPHER_PROMPT_TEMPLATE = (
    "Design a stunning, modern 2D vector illustration featuring the official Golang (Go) Gopher mascot. "
    "CHARACTER DESIGN (CRITICAL): The Gopher must be strictly depicted as a cute, bean-shaped, light cyan-blue creature. "
    "It has large, bulbous white eyes with small black pupils pointing independently, two very prominent white upper buck teeth overlapping the bottom lip, oval-shaped small ears, and stubby limbs. "
    "SCENE & CONTEXT: The Gopher is actively interacting with elements that vividly represent the financial category: '{{category_name}}'. "
    "Additional context: {{category_context}}. "
    "STYLE: Clean, corporate flat vector art. Vibrant, modern tech color palette. Solid or softly gradient minimal background, UI-friendly, visually striking, with no text."
)

@pytest.mark.integration
class TestTransactionFlow:
    def test_create_transaction_existing_category(self, transaction_client, ai_client, auth_session):
        """
        Scenario: Create transaction from AI description using an existing category
        """
        ai_client.create_base_prompt(BasePromptRequest(key=PROMPT_KEY_TX_EXTRACTION, template="Extract tx data from: {{description}}").model_dump(), **auth_session)
        ai_client.create_base_prompt(BasePromptRequest(key=PROMPT_KEY_CAT_DETERMINATION, template="Determine category for: {{title}}").model_dump(), **auth_session)
        ai_client.create_base_prompt(BasePromptRequest(key=PROMPT_KEY_CAT_IMAGE_GEN, template=GOPHER_PROMPT_TEMPLATE).model_dump(), **auth_session)
        
        payload = TransactionAIPayloadRequest(
            description="Compré dos hamburguesas y un refresco por 15 dolares en McDonalds"
        ).model_dump()
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        
        assert res.status_code == HTTPStatus.CREATED
        tx_resp = TransactionResponseModel(**res.json())
        tx_model = tx_resp.data

    def test_create_transaction_new_category_ai(self, transaction_client, ai_client, auth_session):
        """
        Scenario: Create transaction from AI description requiring a new auto-generated category
        """
        ai_client.create_base_prompt(BasePromptRequest(key=PROMPT_KEY_TX_EXTRACTION, template="Extract tx data from: {{description}}").model_dump(), **auth_session)
        ai_client.create_base_prompt(BasePromptRequest(key=PROMPT_KEY_CAT_DETERMINATION, template="Determine category for: {{title}}").model_dump(), **auth_session)
        ai_client.create_base_prompt(BasePromptRequest(key=PROMPT_KEY_CAT_IMAGE_GEN, template=GOPHER_PROMPT_TEMPLATE).model_dump(), **auth_session)

        payload = TransactionAIPayloadRequest(
            description="Paid $50 for a completely new unknown subscription service"
        ).model_dump()
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        assert res.status_code == HTTPStatus.CREATED

        tx_resp = TransactionResponseModel(**res.json())
        tx_model = tx_resp.data

    @pytest.mark.parametrize("scenario,payload,expected", [
        ("AI extraction failure", TransactionAIPayloadRequest(description="asdf123 xyz").model_dump(), HTTPStatus.CREATED),
        ("missing extraction prompt", {}, HTTPStatus.BAD_REQUEST)
    ])
    def test_create_transaction_failures(self, transaction_client, auth_session, scenario, payload, expected):
        res = transaction_client.create_from_ai_description(payload, **auth_session)
        
        assert res.status_code == expected

