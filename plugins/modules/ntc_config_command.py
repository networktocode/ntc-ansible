#!/usr/bin/python

# -*- coding: utf-8 -*-

#  Copyright 2022 Network to Code
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
module: ntc_config_command
short_description: Writes config data to devices
description:
  - This module write config data to devices.
    The use case would be writing configuration based on output gleaned from ntc_show_command output.
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
      platform: "cisco_nxos"
      connection: ssh

- name: Write vlan data
  networktocode.netauto.ntc_config_command:
    connection: ssh
    platform: cisco_nxos
    commands:
      - vlan 10
      - name vlan_10
      - end
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"

- name: Write config from file
  networktocode.netauto.ntc_config_command:
    connection: ssh
    platform: cisco_nxos
    commands_file: "dynamically_created_config.txt"
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"

- name: Configure vlans
  networktocode.netauto.ntc_config_command:
    commands:
      - vlan 10
      - name vlan_10
      - end
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


def error_params(platform, command_output):
    """Checks for typical cisco command error outputs."""
    if "cisco_ios" in platform:
        if "Invalid input detected at '^' marker" in command_output:
            return True
        if "Ambiguous command" in command_output:
            return True
    return False


def main():  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Main execution."""
    base_argument_spec = dict(
        commands=dict(required=True, type="list"),
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
        module.fail_json(msg="pyntc Python library not found.")

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
    # device.config()
    device.close()


if __name__ == "__main__":
    main()
