import pytest
from app.validators.validators import ContextValidator, FlowValidationError


@pytest.mark.parametrize("context,should_pass", [
    ({"user_id": "abc123"}, True),  # Valid context
    ("not a dict", False),          # Not a dictionary
    ({123: "value"}, False),        # Non-string key
    ({"data": "x" * (1024 * 1024 + 1)}, False),  # Oversized context
])
def test_context_validator(context, should_pass):
    if should_pass:
        try:
            ContextValidator.validate_execution_context(context)
        except Exception:
            pytest.fail("Validation was expected to pass but failed.")
    else:
        with pytest.raises(FlowValidationError):
            ContextValidator.validate_execution_context(context)