from unittest.mock import patch

import pytest

from app.core.exceptions import (
    ExternalServiceError,
    ModelResponseError,
)
from app.llm.bedrock import (
    _call_bedrock_with_retry,
    extract_json,
)
from app.llm.prompts import (
    QUOTE_PARSER_SYSTEM_PROMPT,
)


@patch(
    "app.llm.bedrock._call_bedrock"
)
@patch(
    "app.llm.bedrock.time.sleep"
)
def test_bedrock_retries_then_succeeds(
    mock_sleep,
    mock_call,
):
    mock_call.side_effect = [
        ExternalServiceError(
            "temporary failure"
        ),
        {
            "output": {
                "message": {
                    "content": [
                        {
                            "text": "{}"
                        }
                    ]
                }
            }
        },
    ]

    result = _call_bedrock_with_retry(
        "test",
        QUOTE_PARSER_SYSTEM_PROMPT,
    )

    assert result is not None
    assert mock_call.call_count == 2
    assert mock_sleep.call_count == 1


@patch(
    "app.llm.bedrock._call_bedrock"
)
@patch(
    "app.llm.bedrock.time.sleep"
)
def test_bedrock_fails_after_retries(
    mock_sleep,
    mock_call,
):
    mock_call.side_effect = (
        ExternalServiceError(
            "temporary failure"
        )
    )

    with pytest.raises(
        ExternalServiceError
    ):
        _call_bedrock_with_retry(
            "test",
            QUOTE_PARSER_SYSTEM_PROMPT,
        )

    assert mock_call.call_count == 3
    assert mock_sleep.call_count == 2


def test_invalid_model_json_is_not_retryable():
    with pytest.raises(
        ModelResponseError
    ):
        extract_json(
            "This is not JSON"
        )