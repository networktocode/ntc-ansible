# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Network to Code (@networktocode) <info@networktocode.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Nautobot Action Plugin for netcompare."""

from __future__ import (absolute_import, division, print_function)

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.module_utils.six import raise_from

try:
    from netcompare import evaluate_check
except ImportError as imp_exc:
    NC_IMPORT_ERROR = imp_exc
else:
    NC_IMPORT_ERROR = None


__metaclass__ = type


def main(args):
    """Module function."""
    if "evaluate_args" not in args:
        raise AnsibleError("Invalid arguments, 'evaluate_args' not found.")

    eval_results, passed = evaluate_check(args["collection_name"], args["check"], **args["evaluate_args"])
    return dict(
        success=passed,
        fail_details=eval_results,
    )


class ActionModule(ActionBase):
    """Ansible Action Module to interact with netcompare.
    Args:
        ActionBase (ActionBase): Ansible Action Plugin
    """

    def run(self, tmp=None, task_vars=None):
        """Run of action plugin for interacting with netcompare.
        Args:
            tmp ([type], optional): [description]. Defaults to None.
            task_vars ([type], optional): [description]. Defaults to None.
        """
        if NC_IMPORT_ERROR:
            raise_from(
                AnsibleError("netcompare must be installed to use this plugin"),
                NC_IMPORT_ERROR,
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
