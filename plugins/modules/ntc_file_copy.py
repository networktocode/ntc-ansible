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
module: ntc_file_copy
short_description: Copy a file to a remote network device over SCP
description:
    - Copy a file to the flash (or bootflash) remote network device on supported platforms over SCP.
    - Supported platforms include Cisco Nexus switches with NX-API, Cisco IOS switches or routers, Arista switches with eAPI.
notes:
    - On NXOS, the feature must be enabled with feature scp-server.
    - On IOS and Arista EOS, the user must be at privelege 15.
    - If the file is already present (md5 sums match), no transfer will take place.
    - Check mode will tell you if the file would be copied.
    - The same user credentials are used on the API/SSH channel and the SCP file transfer channel.
author: Jason Edelman (@jedelman8)
version_added: 1.9.2
requirements:
    - pyntc
extends_documentation_fragment:
  - networktocode.netauto.netauto
options:
  local_file:
      description:
          - Path to local file. Local directory must exist.
      required: false
      type: str
  remote_file:
      description:
          - Remote file path of the copy. Remote directories must exist.
            If omitted, the name of the local file will be used.
      required: false
      default: null
      type: str
  file_system:
      description:
          - The remote file system of the device. If omitted,
            devices that support a file_system parameter will use their default values.
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

- name: copy file to network device
  networktocode.netauto.ntc_file_copy:
    platform: cisco_nxos_nxapi
    local_file: /path/to/file
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    transport: http
- name: copy file to network device
  networktocode.netauto.ntc_file_copy:
    ntc_host: n9k1
    ntc_conf_file: .ntc.conf
    local_file: /path/to/file
- name: copy file to network device
  networktocode.netauto.ntc_file_copy:
    ntc_host: eos_leaf
    local_file: /path/to/file
- name: copy file to network device
  networktocode.netauto.ntc_file_copy:
    platform: arista_eos_eapi
    local_file: /path/to/file
    remote_file: /path/to/remote_file
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
- name: copy file to network device
  networktocode.netauto.ntc_file_copy:
    platform: cisco_ios
    local_file: "{{ local_file_1 }}"
    provider: "{{ nxos_provider }}"
"""

RETURN = r"""
transfer_status:
    description: Whether a file was transfered. "No Transfer" or "Sent".
    returned: success
    type: str
    sample: 'Sent'
local_file:
    description: The path of the local file.
    returned: success
    type: str
    sample: '/path/to/local/file'
remote_file:
    description: The path of the remote file.
    returned: success
    type: str
    sample: '/path/to/remote/file'
atomic:
    description: Whether the module has atomically completed all steps,
                 including closing connection after file delivering.
    returned: always
    type: bool
    sample: true
"""

import os

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
        global_delay_factor=dict(default=1, required=False, type="int"),
        delay_factor=dict(default=1, required=False, type="int"),
        local_file=dict(required=False),
        remote_file=dict(required=False),
        file_system=dict(required=False),
    )
    argument_spec = base_argument_spec
    argument_spec.update(CONNECTION_ARGUMENT_SPEC)
    argument_spec["provider"] = dict(required=False, type="dict", options=CONNECTION_ARGUMENT_SPEC)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=MUTUALLY_EXCLUSIVE,
        required_one_of=[REQUIRED_ONE_OF],
        supports_check_mode=True,
    )

    provider = module.params["provider"] or {}

    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) is not False:
            module.params[param] = module.params.get(param) or pvalue

    if not HAS_PYNTC:
        module.fail_json(msg="pyntc is required for this module.")

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
        if global_delay_factor is not None:
            kwargs["global_delay_factor"] = global_delay_factor
        if delay_factor is not None:
            kwargs["delay_factor"] = delay_factor

        device_type = platform
        device = ntc_device(device_type, host, username, password, **kwargs)

    local_file = module.params["local_file"]
    remote_file = module.params["remote_file"]
    file_system = module.params["file_system"]

    argument_check = {
        "host": host,
        "username": username,
        "platform": platform,
        "password": password,
        "local_file": local_file,
    }
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    device.open()

    changed = False
    transfer_status = "No Transfer"
    file_exists = True

    if not os.path.isfile(local_file):
        module.fail_json(msg="Local file {0} not found".format(local_file))

    if file_system:
        remote_exists = device.file_copy_remote_exists(local_file, remote_file, file_system=file_system)
    else:
        remote_exists = device.file_copy_remote_exists(local_file, remote_file)

    if not remote_exists:
        changed = True
        file_exists = False

    if not module.check_mode and not file_exists:
        try:
            if file_system:
                device.file_copy(local_file, remote_file, file_system=file_system)
            else:
                device.file_copy(local_file, remote_file)

            transfer_status = "Sent"
        except Exception as err:  # pylint: disable=broad-except
            module.fail_json(msg=str(err))

    try:
        device.close()
        atomic = True
    except:  # noqa
        atomic = False

    if remote_file is None:
        remote_file = os.path.basename(local_file)

    module.exit_json(
        changed=changed,
        transfer_status=transfer_status,
        local_file=local_file,
        remote_file=remote_file,
        file_system=file_system,
        atomic=atomic,
    )


if __name__ == "__main__":
    main()
