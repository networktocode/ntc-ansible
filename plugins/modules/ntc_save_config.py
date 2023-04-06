#!/usr/bin/python

# Copyright 2015 Jason Edelman <jason@networktocode.com>
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
module: ntc_save_config
short_description: Save the running config locally and/or remotely
description:
    - Save the running configuration as the startup configuration or to a file on the network device.
      Optionally, save the running configuration to this computer.
    - Supported platforms include Cisco Nexus switches with NX-API, Cisco IOS switches or routers, Arista switches with eAPI.
notes:
    - This module is not idempotent.
author: Jason Edelman (@jedelman8)
version_added: 1.9.2
requirements:
    - pyntc
extends_documentation_fragment:
  - networktocode.netauto.netauto
options:
    remote_file:
        description:
            - Name of remote file to save the running configuration. If omitted it will be
              saved to the startup configuration.
        required: false
        default: null
        type: str
    local_file:
        description:
            - Name of local file to save the running configuration. If omitted it won't be locally saved.
        required: false
        default: null
        type: str
    global_delay_factor:
        description:
            - Sets delay between operations.
        required: false
        default: 1
        type: int
    delay_factor:
        description:
            - Multiplication factor for timing delays
        required: false
        default: 1
        type: int
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

- networktocode.netauto.ntc_save_config:
    platform: cisco_nxos_nxapi
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"

- networktocode.netauto.ntc_save_config:
    ntc_host: n9k1

- networktocode.netauto.ntc_save_config:
    platform: arista_eos_eapi
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    remote_file: running_config_copy.cfg
    transport: https

# You can get the timestamp by setting get_facts to True, then you can append it to your filename.

- networktocode.netauto.ntc_save_config:
    provider: "{{ nxos_provider }}"
    local_file: config_{{ inventory_hostname }}_{{ ansible_date_time.date | replace('-','_') }}.cfg
"""

RETURN = r"""
local_file:
    description: The local file path of the saved running config.
    returned: success
    type: str
    sample: '/path/to/config.cfg'
remote_file:
    description: The remote file name of the saved running config.
    returned: success
    type: str
    sample: 'config_backup.cfg'
remote_save_successful:
    description: Whether the remote save was successful.
        May be false if a remote save was unsuccessful because a file with same name already exists.
    returned: success
    type: bool
    sample: true
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.networktocode.netauto.plugins.module_utils.args_common import (
    CONNECTION_ARGUMENT_SPEC,
    MUTUALLY_EXCLUSIVE,
    NETMIKO_BACKEND,
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
        global_delay_factor=dict(default=1, required=False, type="int"),
        delay_factor=dict(default=1, required=False, type="int"),
        remote_file=dict(required=False, type="str"),
        local_file=dict(required=False, type="str"),
    )
    argument_spec = base_argument_spec
    argument_spec.update(CONNECTION_ARGUMENT_SPEC)
    argument_spec["provider"] = dict(required=False, type="dict", options=CONNECTION_ARGUMENT_SPEC)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=MUTUALLY_EXCLUSIVE,
        required_one_of=[REQUIRED_ONE_OF],
        supports_check_mode=False,
    )

    if not HAS_PYNTC:
        module.fail_json(msg="pyntc is required for this module.")

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
    global_delay_factor = int(module.params["global_delay_factor"])
    delay_factor = int(module.params["delay_factor"])
    secret = module.params["secret"]

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
        if platform in NETMIKO_BACKEND:
            if global_delay_factor is not None:
                kwargs["global_delay_factor"] = global_delay_factor
            if delay_factor is not None:
                kwargs["delay_factor"] = delay_factor

        device_type = platform
        device = ntc_device(device_type, host, username, password, **kwargs)

    remote_file = module.params["remote_file"]
    local_file = module.params["local_file"]

    argument_check = {"host": host, "username": username, "platform": platform, "password": password}
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    device.open()

    if remote_file:
        remote_save_successful = device.save(remote_file)
    else:
        remote_save_successful = device.save()

    changed = remote_save_successful
    if local_file:
        device.backup_running_config(local_file)
        changed = True

    device.close()

    remote_file = remote_file or "(Startup Config)"
    module.exit_json(
        changed=changed, remote_save_successful=remote_save_successful, remote_file=remote_file, local_file=local_file
    )


if __name__ == "__main__":
    main()
