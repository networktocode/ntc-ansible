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
module: ntc_rollback
short_description: Set a checkpoint or rollback to a checkpoint
description:
    - This module offers the ability to set a configuration checkpoint file or rollback
      to a configuration checkpoint file on supported Cisco or Arista switches.
notes:
    - This module is not idempotent.
author: Jason Edelman (@jedelman8)
requirements:
    - pyntc
extends_documentation_fragment:
  - networktocode.netauto.netauto
options:
    checkpoint_file:
        description:
            - Name of checkpoint file to create. Mutually exclusive with rollback_to.
        required: false
        default: null
        type: str
    rollback_to:
        description:
            - Name of checkpoint file to rollback to. Mutually exclusive with checkpoint_file.
        required: false
        default: null
        type: str
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

- networktocode.netoauto.ntc_rollback:
    provider: "{{ nxos_provider }}"
    rollback_to: backup.cfg

- networktocode.netoauto.ntc_rollback:
    ntc_host: eos1
    checkpoint_file: backup.cfg

- networktocode.netoauto.ntc_rollback:
    ntc_host: eos1
    rollback_to: backup.cfg
"""

RETURN = r"""
filename:
    description: The filename of the checkpoint/rollback file.
    returned: success
    type: str
    sample: 'backup.cfg'
status:
    description: Which operation took place and whether it was successful.
    returned: success
    type: str
    sample: 'rollback executed'
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

UNSUPPORTED_PLATFORMS = ["cisco_aireos_ssh", "f5_tmos_icontrol"]


def main():  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Main execution."""
    base_argument_spec = dict(
        checkpoint_file=dict(required=False, type="str"),
        rollback_to=dict(required=False, type="str"),
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
    secret = module.params["secret"]

    if platform in UNSUPPORTED_PLATFORMS:
        module.fail_json(msg=f"ntc_rollback is not implemented for this platform type {platform}.")

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

    checkpoint_file = module.params["checkpoint_file"]
    rollback_to = module.params["rollback_to"]

    argument_check = {"host": host, "username": username, "platform": platform, "password": password}
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    device.open()

    status = None
    filename = None
    changed = False
    try:
        if checkpoint_file:
            device.checkpoint(checkpoint_file)
            status = "checkpoint file created"
        elif rollback_to:
            device.rollback(rollback_to)
            status = "rollback executed"
        changed = True
        filename = rollback_to or checkpoint_file
    except Exception as e:  # pylint: disable=broad-except
        module.fail_json(msg=str(e))

    device.close()
    module.exit_json(changed=changed, status=status, filename=filename)


if __name__ == "__main__":
    main()
