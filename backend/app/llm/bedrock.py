import json
import re
import time

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import ValidationError

from app.core.config import settings
from app.llm.prompts import QUOTE_PARSER_SYSTEM_PROMPT
from app.monitoring.logger import logger
from app.schemas.ai import ParsedQuoteRequest


bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name=settings.aws_region,
)


def extract_json(text: str) -> dict:
    """
    Extract a JSON object from the model response.

    Handles responses that contain markdown code fences
    or additional text around the JSON object.
    """

    text = text.strip()

    # Remove ```json ... ``` or ``` ... ``` wrappers
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

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "AI response did not contain a JSON object"
            )

        json_text = text[start:end + 1]

        return json.loads(json_text)


def parse_quote_request(
    message: str,
) -> ParsedQuoteRequest:

    try:
        logger.info(
            "Sending quote parsing request to Bedrock"
        )

        start_time = time.perf_counter()

        response = bedrock_client.converse(
            modelId=settings.bedrock_model_id,
            system=[
                {
                    "text": QUOTE_PARSER_SYSTEM_PROMPT
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

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "Bedrock request completed in %.2f ms",
            elapsed_ms,
        )

        text = (
            response["output"]["message"]["content"][0]["text"]
        )

        parsed_json = extract_json(text)

        parsed_request = ParsedQuoteRequest.model_validate(
            parsed_json
        )

        logger.info(
            "Quote request parsed successfully"
        )

        return parsed_request

    except json.JSONDecodeError as exc:
        logger.error(
            "Bedrock returned invalid JSON"
        )

        raise ValueError(
            "AI returned invalid JSON"
        ) from exc

    except ValidationError as exc:
        logger.error(
            "Bedrock response failed schema validation"
        )

        raise ValueError(
            "AI response did not match the expected schema"
        ) from exc

    except (BotoCoreError, ClientError) as exc:
        logger.error(
            "Bedrock request failed: %s",
            exc,
        )

        raise RuntimeError(
            "Bedrock request failed"
        ) from exc