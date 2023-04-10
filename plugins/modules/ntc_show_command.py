#!/usr/bin/python

# Copyright 2022 Network to Code
# Network to Code, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ntc_show_command
short_description: Gets output from show commands and tries to return structured data
description:
    - This module connects to network devices using SSH and tries to
      return structured data (JSON).
author: "Jeff Kala (@jeffkala)"
requirements:
    - pyntc
extends_documentation_fragment:
  - networktocode.netauto.netauto
  - networktocode.netauto.netauto.command_option

"""
EXAMPLES = r"""
- hosts: all
  vars:
    nxos_provider:
      host: "{{ inventory_hostname }}"
      username: "ntc-ansible"
      password: "ntc-ansible"
      platform: "cisco_nxos_nxapi"
      connection: local

- name: Get Vlans
  networktocode.netauto.ntc_show_command:
    connection: local
    platform: cisco_nxos
    commands:
      - show vlans
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"

- name: Get Vlans
  networktocode.netauto.ntc_show_command:
    commands:
      - show vlans
    provider: "{{ nxos_provider }}"

- name: Get From a File
  networktocode.netauto.ntc_show_command:
    commands_file: "list_of_cmds.txt"
    provider: "{{ nxos_provider }}"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.networktocode.netauto.plugins.module_utils.args_common import (
    CONNECTION_ARGUMENT_SPEC,
    MUTUALLY_EXCLUSIVE,
    REQUIRED_ONE_OF,
)

try:
    HAS_PYNTC = True
    from pyntc import ntc_device, ntc_device_by_name
except ImportError:
    HAS_PYNTC = False


def main():  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Main execution."""
    base_argument_spec = dict(
        commands=dict(required=False, type="list"),
        commands_file=dict(required=False, default=None, type="str"),
    )
    argument_spec = base_argument_spec
    argument_spec.update(CONNECTION_ARGUMENT_SPEC)
    argument_spec["provider"] = dict(required=False, type="dict", options=CONNECTION_ARGUMENT_SPEC)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        mutually_exclusive=MUTUALLY_EXCLUSIVE,
        required_one_of=[REQUIRED_ONE_OF],
    )

    if not HAS_PYNTC:
        module.fail_json(msg="pyntc is required for this module.")

    if not any([module.params["commands"], module.params["commands_file"]]):
        module.fail_json(msg="One of `commands` or `commands_file` argument is required.")

    if module.params["commands"] and module.params["commands_file"]:
        module.fail_json(
            msg="The use of both `commands` and `commands_file` in the same task is not currently supported."
        )
    elif module.params["commands_file"]:
        with open(module.params["commands_file"], "r") as cmds:
            commands = [cmd.rstrip() for cmd in cmds]
    elif module.params["commands"]:
        commands = module.params["commands"]
    else:
        module.fail_json(msg="The combination of params used is not supported.")

    provider = module.params["provider"] or {}

    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) is not False:
            module.params[param] = module.params.get(param) or pvalue

    platform = module.params["platform"]
    host = module.params["host"]
    username = module.params["username"]
    password = module.params["password"]

    ntc_host = module.params["ntc_host"]
    ntc_conf_file = module.params["ntc_conf_file"]

    transport = module.params["transport"]
    port = module.params["port"]
    secret = module.params["secret"]

    argument_check = {"host": host, "username": username, "platform": platform, "password": password}
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    if ntc_host is not None:
        device = ntc_device_by_name(ntc_host, ntc_conf_file)
    else:
        kwargs = {}
        if transport is not None:
            kwargs["transport"] = transport
        if port is not None:
            kwargs["port"] = port
        if secret is not None:
            kwargs["secret"] = secret

        device_type = platform
        device = ntc_device(device_type, host, username, password, **kwargs)

    device.open()
    result = device.show(commands)
    device.close()

    module.exit_json(
        changed=False,
        results=result,
    )


if __name__ == "__main__":
    main()
