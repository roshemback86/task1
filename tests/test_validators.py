import pytest
from app.validators.validators import ContextValidator, FlowValidationError


def test_context_validator_valid():
    """Should pass for a well-formed context dictionary."""
    valid_context = {"user_id": "abc123"}
    try:
        ContextValidator.validate_execution_context(valid_context)
    except Exception:
        pytest.fail("Validation was expected to pass but raised an exception.")


def test_context_validator_invalid():
    """Should raise error for context with non-string key."""
    invalid_context = {123: "invalid_key"}  # Invalid: numeric key
    with pytest.raises(FlowValidationError):
        ContextValidator.validate_execution_context(invalid_context)