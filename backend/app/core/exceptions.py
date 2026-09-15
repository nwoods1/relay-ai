class WorkflowError(Exception):
    """Base exception for workflow failures."""


class RetryableWorkflowError(WorkflowError):
    """Failure that may succeed if retried."""


class NonRetryableWorkflowError(WorkflowError):
    """Failure that should not be retried."""


class ExternalServiceError(RetryableWorkflowError):
    """Temporary external service failure."""


class ModelResponseError(NonRetryableWorkflowError):
    """Model returned malformed or unusable output."""


class BusinessRuleError(NonRetryableWorkflowError):
    """Business request cannot be completed."""