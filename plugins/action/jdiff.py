# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Network to Code (@networktocode) <info@networktocode.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Nautobot Action Plugin for jdiff."""

from __future__ import (absolute_import, division, print_function)

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.module_utils.six import raise_from

try:
    from jdiff import CheckType, extract_data_from_json
except ImportError as imp_exc:
    JDIFF_IMPORT_ERROR = imp_exc
else:
    JDIFF_IMPORT_ERROR = None


__metaclass__ = type


def main(args):
    """Module function."""
    if "evaluate_args" not in args:
        raise AnsibleError("Invalid arguments, 'evaluate_args' not found.")
    check_type = args.get('check_type')
    evaluate_args = args.get('evaluate_args')
    if not isinstance(evaluate_args, dict):
        raise AnsibleError(f"'evaluate_args' invalid type, expected <class 'dict'>, got {type(evaluate_args)}")
    if "value_to_compare" not in evaluate_args:
        raise AnsibleError("Key 'value_to_compare' missing in 'evaluate_arguments'.")
    reference_data = evaluate_args.get("reference_data")
    value = evaluate_args['value_to_compare']
    jpath = args.get('jmespath', '*')
    exclude = args.get('exclude')

    try:
        check = CheckType.create(check_type)
        evaluate_args['value_to_compare'] = extract_data_from_json(value, jpath, exclude)
        if reference_data:
            evaluate_args['reference_data'] = extract_data_from_json(reference_data, jpath, exclude)
        eval_results, passed = check.evaluate(**evaluate_args)
    except NotImplementedError:
        raise AnsibleError(f"CheckType '{check_type}' not supported by jdiff")
    except Exception as e:
        raise AnsibleError(f"Exception in backend jdiff library: {e}")

    return dict(
        success=passed,
        fail_details=eval_results,
    )


class ActionModule(ActionBase):
    """Ansible Action Module to interact with jdiff.
    Args:
        ActionBase (ActionBase): Ansible Action Plugin
    """

    def run(self, tmp=None, task_vars=None):
        """Run of action plugin for interacting with jdiff.
        Args:
            tmp ([type], optional): [description]. Defaults to None.
            task_vars ([type], optional): [description]. Defaults to None.
        """
        if JDIFF_IMPORT_ERROR:
            raise_from(
                AnsibleError("jdiff library must be installed to use this plugin"),
                JDIFF_IMPORT_ERROR,
            )

        self._supports_check_mode = True
        self._supports_async = False

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp

        if result.get("skipped"):
            return None

        if result.get("invocation", {}).get("module_args"):
            # avoid passing to modules in case of no_log
            # should not be set anymore but here for backwards compatibility
            del result["invocation"]["module_args"]

        args = self._task.args
        return main(args=args)
