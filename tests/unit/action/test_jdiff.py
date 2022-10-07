"""Tests for jdiff Action Plugin."""
from ansible.errors import AnsibleError
import pytest


try:
    from plugins.action.jdiff import main
except ImportError:
    import sys

    sys.path.append("tests")
    sys.path.append("plugins/action")

    from jdiff import main


def test_valid_args():
    args = {
        "check_type": "exact_match",
        "evaluate_args": {
            "value_to_compare": "",
            "reference_data": ""
        }
    }
    result = main(args)
    assert result == {'success': True, 'fail_details': {}}


def test_invalid_args_empty_args():
    with pytest.raises(AnsibleError) as exc:
        main({})
    assert str(exc.value) == "Invalid arguments, 'evaluate_args' not found."


def test_invalid_args_unsupported_checktype():
    args = {
        "check_type": "unknown",
        "evaluate_args": {
            "value_to_compare": "",
            "reference_data": ""
        }
    }
    with pytest.raises(AnsibleError) as exc:
        main(args)
    assert str(exc.value) == "CheckType 'unknown' not supported by jdiff"


def test_invalid_args_evaluate_args_wrong_type():
    args = {
        "evaluate_args": []
    }
    with pytest.raises(AnsibleError) as exc:
        main(args)
    assert str(exc.value) == "'evaluate_args' invalid type, expected <class 'dict'>, got <class 'list'>"


def test_invalid_args_no_value_to_compare():
    args = {
        "evaluate_args": {}
    }
    with pytest.raises(AnsibleError) as exc:
        main(args)
    assert str(exc.value) == "Key 'value_to_compare' missing in 'evaluate_arguments'."
