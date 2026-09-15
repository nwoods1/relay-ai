import json
import re
import time

import boto3
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    ConnectTimeoutError,
    EndpointConnectionError,
    ReadTimeoutError,
)
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import (
    ExternalServiceError,
    ModelResponseError,
)
from app.llm.prompts import QUOTE_PARSER_SYSTEM_PROMPT
from app.monitoring.logger import logger
from app.schemas.ai import ParsedQuoteRequest


BEDROCK_MAX_ATTEMPTS = 3
BEDROCK_RETRY_DELAY_SECONDS = 0.5


bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name=settings.aws_region,
    config=Config(
        connect_timeout=5,
        read_timeout=20,
        retries={
            "max_attempts": 1,
            "mode": "standard",
        },
    ),
)


def extract_json(text: str) -> dict:
    """
    Extract a JSON object from the model response.

    Handles responses that contain markdown code fences
    or additional text around the JSON object.
    """

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if (
            start == -1
            or end == -1
            or end <= start
        ):
            raise ModelResponseError(
                "AI response did not contain a JSON object"
            )

        json_text = text[
            start:end + 1
        ]

        try:
            return json.loads(
                json_text
            )

        except json.JSONDecodeError as exc:
            raise ModelResponseError(
                "AI returned invalid JSON"
            ) from exc


def _call_bedrock(
    message: str,
) -> dict:

    try:
        return bedrock_client.converse(
            modelId=settings.bedrock_model_id,
            system=[
                {
                    "text":
                        QUOTE_PARSER_SYSTEM_PROMPT
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": message
                        }
                    ],
                }
            ],
            inferenceConfig={
                "temperature": 0,
                "maxTokens": 300,
            },
        )

    except (
        ConnectTimeoutError,
        ReadTimeoutError,
        EndpointConnectionError,
        BotoCoreError,
    ) as exc:
        raise ExternalServiceError(
            "Temporary Bedrock connection failure"
        ) from exc

    except ClientError as exc:
        status_code = (
            exc.response
            .get("ResponseMetadata", {})
            .get("HTTPStatusCode")
        )

        if (
            status_code is not None
            and status_code >= 500
        ):
            raise ExternalServiceError(
                "Temporary Bedrock service failure"
            ) from exc

        raise ModelResponseError(
            "Bedrock request was rejected"
        ) from exc


def _call_bedrock_with_retry(
    message: str,
) -> dict:

    last_error = None

    for attempt in range(
        1,
        BEDROCK_MAX_ATTEMPTS + 1,
    ):
        try:
            logger.info(
                "Bedrock attempt %s/%s",
                attempt,
                BEDROCK_MAX_ATTEMPTS,
            )

            return _call_bedrock(
                message
            )

        except ExternalServiceError as exc:
            last_error = exc

            logger.warning(
                "Bedrock attempt %s failed: %s",
                attempt,
                exc,
            )

            if (
                attempt
                == BEDROCK_MAX_ATTEMPTS
            ):
                break

            delay = (
                BEDROCK_RETRY_DELAY_SECONDS
                * attempt
            )

            time.sleep(
                delay
            )

    raise ExternalServiceError(
        "Bedrock request failed after retries"
    ) from last_error


def parse_quote_request(
    message: str,
) -> ParsedQuoteRequest:

    logger.info(
        "Sending quote parsing request to Bedrock"
    )

    start_time = time.perf_counter()

    response = _call_bedrock_with_retry(
        message
    )

    elapsed_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    logger.info(
        "Bedrock request completed in %.2f ms",
        elapsed_ms,
    )

    try:
        text = (
            response[
                "output"
            ][
                "message"
            ][
                "content"
            ][0][
                "text"
            ]
        )

    except (
        KeyError,
        IndexError,
        TypeError,
    ) as exc:
        raise ModelResponseError(
            "Bedrock response had an unexpected structure"
        ) from exc

    parsed_json = extract_json(
        text
    )

    try:
        parsed_request = (
            ParsedQuoteRequest.model_validate(
                parsed_json
            )
        )

    except ValidationError as exc:
        logger.error(
            "Bedrock response failed schema validation"
        )

        raise ModelResponseError(
            "AI response did not match the expected schema"
        ) from exc

    logger.info(
        "Quote request parsed successfully"
    )

    return parsed_request