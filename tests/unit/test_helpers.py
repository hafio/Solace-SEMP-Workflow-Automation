"""Unit tests for semp/helpers.py."""

import pytest

from semp_workflow.semp.helpers import (
    check_name_length,
    clean_payload,
    coerce_bool,
    coerce_int,
    enc,
)


class TestCoerceBool:
    def test_true_passthrough(self):
        assert coerce_bool(True) is True

    def test_false_passthrough(self):
        assert coerce_bool(False) is False

    def test_string_true(self):
        assert coerce_bool("true") is True

    def test_string_True(self):
        assert coerce_bool("True") is True

    def test_string_yes(self):
        assert coerce_bool("yes") is True

    def test_string_1(self):
        assert coerce_bool("1") is True

    def test_string_false(self):
        assert coerce_bool("false") is False

    def test_string_no(self):
        assert coerce_bool("no") is False

    def test_string_0(self):
        assert coerce_bool("0") is False

    def test_string_empty(self):
        assert coerce_bool("") is False

    def test_int_nonzero(self):
        assert coerce_bool(1) is True

    def test_int_zero(self):
        assert coerce_bool(0) is False


class TestCoerceInt:
    def test_int_passthrough(self):
        assert coerce_int(42) == 42

    def test_zero(self):
        assert coerce_int(0) == 0

    def test_negative(self):
        assert coerce_int(-1) == -1

    def test_string_int(self):
        assert coerce_int("42") == 42

    def test_string_zero(self):
        assert coerce_int("0") == 0

    def test_bool_true_raises(self):
        # bool is excluded from int passthrough; "True" cannot be parsed
        with pytest.raises((ValueError, TypeError)):
            coerce_int(True)

    def test_string_abc_raises(self):
        with pytest.raises((ValueError, TypeError)):
            coerce_int("abc")


class TestCheckNameLength:
    def test_within_limit(self):
        assert check_name_length("queueName", "short") is None

    def test_at_exact_limit(self):
        assert check_name_length("queueName", "x" * 200) is None

    def test_over_limit(self):
        result = check_name_length("queueName", "x" * 201)
        assert result is not None
        assert "201" in result
        assert "200" in result

    def test_unknown_field(self):
        assert check_name_length("unknownField", "x" * 9999) is None

    def test_restConsumerName_limit(self):
        assert check_name_length("restConsumerName", "x" * 32) is None
        result = check_name_length("restConsumerName", "x" * 33)
        assert result is not None

    def test_aclProfileName_limit(self):
        assert check_name_length("aclProfileName", "x" * 32) is None
        result = check_name_length("aclProfileName", "x" * 33)
        assert result is not None


class TestCleanPayload:
    def test_removes_none(self):
        result = clean_payload({"a": None, "b": "value"})
        assert "a" not in result
        assert result["b"] == "value"

    def test_removes_empty_string(self):
        result = clean_payload({"a": "", "b": "value"})
        assert "a" not in result

    def test_removes_whitespace_only_string(self):
        result = clean_payload({"a": "  ", "b": "value"})
        assert "a" not in result

    def test_keeps_zero(self):
        result = clean_payload({"a": 0})
        assert result["a"] == 0

    def test_keeps_false(self):
        result = clean_payload({"a": False})
        assert result["a"] is False

    def test_keeps_valid_string(self):
        result = clean_payload({"a": "hello"})
        assert result["a"] == "hello"

    def test_empty_dict(self):
        assert clean_payload({}) == {}

    def test_returns_copy(self):
        original = {"a": "x"}
        result = clean_payload(original)
        result["b"] = "y"
        assert "b" not in original


class TestEnc:
    def test_slash_encoded(self):
        assert "/" not in enc("a/b")

    def test_hash_encoded(self):
        assert "#" not in enc("a#b")

    def test_asterisk_encoded(self):
        assert "*" not in enc("a*b")

    def test_gt_encoded(self):
        assert ">" not in enc("a>b")

    def test_alphanumeric_unchanged(self):
        assert enc("abc123") == "abc123"

    def test_space_encoded(self):
        assert " " not in enc("a b")

    def test_dead_msg_queue(self):
        # #DEAD_MSG_QUEUE contains a # that must be encoded
        result = enc("#DEAD_MSG_QUEUE")
        assert "#" not in result
