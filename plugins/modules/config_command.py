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
short_description: Writes config data to devices that don't have an API
description:
    - This module write config data to devices that don't have an API.
      The use case would be writing configuration based on output gleaned
      from ntc_show_command output.
author: "Jeff Kala"
requirements:
    - pyntc
options:
    platform:
        description:
            - Switch platform
        required: false
        default: null
        choices: ['cisco_nxos_nxapi', 'arista_eos_eapi', 'cisco_ios_ssh', 'f5_tmos_icontrol']
    host:
        description:
            - Hostame or IP address of switch.
        required: false
        default: null
    username:
        description:
            - Username used to login to the target device
        required: false
        default: null
    password:
        description:
            - Password used to login to the target device
        required: false
        default: null
    provider:
        description:
          - Dictionary which acts as a collection of arguments used to define the characteristics
            of how to connect to the device.
            Note - host, username, password and platform must be defined in either provider
            or local param
            Note - local param takes precedence, e.g. hostname is preferred to provider['host']
        required: false
    secret:
        description:
            - Enable secret for devices connecting over SSH.
        required: false
        default: null
    transport:
        description:
            - Transport protocol for API-based devices.
        required: false
        default: null
        choices: ['http', 'https']
    port:
        description:
            - TCP/UDP port to connect to target device. If omitted standard port numbers will be used.
              80 for HTTP; 443 for HTTPS; 22 for SSH.
        required: false
        default: null
    ntc_host:
        description:
            - The name of a host as specified in an NTC configuration file.
        required: false
        default: null
    ntc_conf_file:
        description:
            - The path to a local NTC configuration file. If omitted, and ntc_host is specified,
              the system will look for a file given by the path in the environment variable PYNTC_CONF,
              and then in the users home directory for a file called .ntc.conf.
        required: false
        default: null
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
# import os.path
# import socket

# from ansible.module_utils.basic import AnsibleModule

# try:
#     from netmiko import ConnectHandler

#     HAS_NETMIKO = True
# except ImportError:
#     HAS_NETMIKO = False

from ansible.module_utils.basic import AnsibleModule

try:
    HAS_PYNTC = True
    from pyntc import ntc_device, ntc_device_by_name
except ImportError:
    HAS_PYNTC = False

PLATFORM_NXAPI = "cisco_nxos_nxapi"
PLATFORM_IOS = "cisco_ios_ssh"
PLATFORM_EAPI = "arista_eos_eapi"
PLATFORM_JUNOS = "juniper_junos_netconf"
PLATFORM_F5 = "f5_tmos_icontrol"


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
    connection_argument_spec = dict(
        platform=dict(
            choices=[PLATFORM_NXAPI, PLATFORM_IOS, PLATFORM_EAPI, PLATFORM_JUNOS, PLATFORM_F5], required=False
        ),
        host=dict(required=False),
        port=dict(required=False),
        username=dict(required=False, type="str"),
        password=dict(required=False, type="str", no_log=True),
        secret=dict(required=False, type="str", no_log=True),
        transport=dict(required=False, choices=["http", "https"]),
        ntc_host=dict(required=False),
        ntc_conf_file=dict(required=False),
    )
    base_argument_spec = {}
    argument_spec = base_argument_spec
    argument_spec.update(connection_argument_spec)
    argument_spec["provider"] = dict(required=False, type="dict", options=connection_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        mutually_exclusive=[
            ["host", "ntc_host"],
            ["ntc_host", "secret"],
            ["ntc_host", "transport"],
            ["ntc_host", "port"],
            ["ntc_conf_file", "secret"],
            ["ntc_conf_file", "transport"],
            ["ntc_conf_file", "port"],
        ],
        required_one_of=[["host", "ntc_host", "provider"]],
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
