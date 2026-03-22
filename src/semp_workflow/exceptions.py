"""Exception hierarchy for SEMP Workflow Automation."""


class WorkflowError(Exception):
    """Base exception for all workflow errors."""


class ConfigError(WorkflowError):
    """Invalid or missing configuration."""


class TemplateError(WorkflowError):
    """Error loading or resolving a workflow template."""


class ValidationError(WorkflowError):
    """Input validation failure."""


class SEMPError(WorkflowError):
    """Error returned by the Solace SEMP API."""

    def __init__(self, message: str, status_code: int = 0, semp_code: int = 0):
        super().__init__(message)
        self.status_code = status_code
        self.semp_code = semp_code
