import pytest
from app.validators.validators import ContextValidator, FlowValidationError


def test_context_validator_valid():
    valid_context = {"user_id": "abc123"}
    try:
        ContextValidator.validate_execution_context(valid_context)
    except Exception:
        pytest.fail("Validation should pass")


def test_context_validator_invalid():
    # Передаём словарь с нестроковым ключом, чтобы вызвать FlowValidationError
    with pytest.raises(FlowValidationError):
        ContextValidator.validate_execution_context({123: "invalid_key"})