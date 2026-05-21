"""Tests unitaires de retry_operation.

Point pédagogique : retry local, synchrone, simple.
- succès immédiat
- succès après retry
- échec après max_attempts
"""
import json
import logging
from unittest.mock import Mock

import pytest

from app.application.common.retry_utils import retry_operation

_logger = logging.getLogger(__name__)

_SUCCESS_RAW = json.dumps({"success": True, "error": None, "data": {"post": "Hello"}})
_OPERATION_NAME = "generate_facebook"


class TestRetrySuccess:

    def test_immediate_success(self):
        operation = Mock(return_value=_SUCCESS_RAW)
        result = retry_operation(operation, logger=_logger, operation_name=_OPERATION_NAME)
        assert result["success"] is True
        assert operation.call_count == 1

    def test_success_after_one_retry(self):
        operation = Mock(side_effect=[RuntimeError("transient"), _SUCCESS_RAW])
        result = retry_operation(operation, logger=_logger, operation_name=_OPERATION_NAME)
        assert result["success"] is True
        assert operation.call_count == 2

    def test_success_after_two_retries(self):
        operation = Mock(side_effect=[RuntimeError("fail"), RuntimeError("fail"), _SUCCESS_RAW])
        result = retry_operation(
            operation, max_attempts=3, logger=_logger, operation_name=_OPERATION_NAME
        )
        assert result["success"] is True
        assert operation.call_count == 3


class TestRetryFailure:

    def test_failure_after_max_attempts(self):
        operation = Mock(side_effect=RuntimeError("API down"))
        result = retry_operation(
            operation, max_attempts=3, logger=_logger, operation_name=_OPERATION_NAME
        )
        assert result["success"] is False
        assert operation.call_count == 3

    def test_error_dict_has_correct_structure(self):
        operation = Mock(side_effect=RuntimeError("timeout"))
        result = retry_operation(
            operation, max_attempts=3, logger=_logger, operation_name=_OPERATION_NAME
        )
        assert result["error"] == "node_execution_failed"
        assert "attempts" in result["data"]
        assert "operation" in result["data"]

    def test_attempts_count_in_error(self):
        operation = Mock(side_effect=RuntimeError("timeout"))
        result = retry_operation(
            operation, max_attempts=2, logger=_logger, operation_name=_OPERATION_NAME
        )
        assert result["data"]["attempts"] == 2

    def test_operation_name_in_error(self):
        operation = Mock(side_effect=RuntimeError("timeout"))
        result = retry_operation(
            operation, max_attempts=1, logger=_logger, operation_name="generate_instagram"
        )
        assert result["data"]["operation"] == "generate_instagram"

    def test_tool_business_error_not_retried(self):
        """Si le tool retourne success=False sans lever d'exception, pas de retry."""
        tool_error = json.dumps({"success": False, "error": "invalid_input_json", "data": {}})
        operation = Mock(return_value=tool_error)
        result = retry_operation(
            operation, max_attempts=3, logger=_logger, operation_name=_OPERATION_NAME
        )
        assert result["success"] is False
        assert result["error"] == "invalid_input_json"
        assert operation.call_count == 1
