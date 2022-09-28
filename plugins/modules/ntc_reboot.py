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
module: ntc_reboot
short_description: Reboot a network device
description:
    - Reboot a network device, optionally on a timer.
Notes:
    - The timer is only supported for IOS devices.
author: Jason Edelman (@jedelman8)
version_added: 1.9.2
requirements:
    - pyntc
extends_documentation_fragment:
  - networktocode.netauto.netauto
options:
    timer:
        description:
            - Time in minutes after which the device will be rebooted.
        required: false
        default: null
        type: int
    timeout:
        description:
            - Time in seconds to wait for the device and API to come back up.
              Uses specified port/protocol as defined with port and protocol params.
        required: false
        default: 240
        type: int
    confirm:
        description:
            - Safeguard boolean. Set to true if you're sure you want to reboot.
        required: false
        default: false
        type: bool
    volume:
        description:
            - Volume name - required argument for F5 platform.
        required: false
        type: str
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

- ntc_reboot:
    provider: "{{ nxos_provider }}"
    confirm: true

- ntc_reboot:
    platform: cisco_nxos_nxapi
    confirm: true
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    transport: http

- ntc_reboot:
    ntc_host: n9k1
    ntc_conf_file: .ntc.conf
    confirm: true

- ntc_reboot:
    platform: arista_eos_eapi
    confirm: true
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"

- ntc_reboot:
    platform: cisco_ios
    confirm: true
    timer: 5
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"
"""

RETURN = r"""
rebooted:
    description: Whether the device was instructed to reboot.
    returned: success
    type: boolean
    sample: true
reachable:
    description: Whether the device is reachable on specified port
                 after rebooting.
    returned: always
    type: boolean
    sample: true
atomic:
    description: Whether the module has atomically completed all steps,
                 including testing port and closing connection after
                 rebooting.
    returned: always
    type: boolean
    sample: true
"""
import time

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

# PLATFORM_NXAPI = "cisco_nxos_nxapi"
PLATFORM_IOS = "cisco_ios_ssh"
# PLATFORM_EAPI = "arista_eos_eapi"
PLATFORM_JUNOS = "juniper_junos_netconf"
PLATFORM_F5 = "f5_tmos_icontrol"
# PLATFORM_ASA = "cisco_asa_ssh"


def check_device(module, username, password, host, timeout, kwargs):  # pylint: disable=too-many-arguments
    """Simple check of the device."""
    success = False
    attempts = timeout / 30
    counter = 0
    atomic = False
    while counter < attempts and not success:
        try:
            if module.params["ntc_host"] is not None:
                device = ntc_device_by_name(module.params["ntc_host"], module.params["ntc_conf_file"])
            else:
                device_type = module.params["platform"]
                device = ntc_device(device_type, host, username, password, **kwargs)
            success = True
            atomic = True
            try:
                device.close()
            except:  # noqa
                atomic = False
        except:  # noqa
            time.sleep(30)
            counter += 1
    return success, atomic


def main():  # pylint: disable=too-many-arguments,too-many-branches,too-many-statements,too-many-locals
    """Main execution."""
    base_argument_spec = dict(
        confirm=dict(required=False, default=True, type="bool"),
        timer=dict(requred=False, type="int"),
        timeout=dict(required=False, type="int", default=240),
        volume=dict(required=False, type="str"),
    )
    argument_spec = base_argument_spec
    argument_spec.update(CONNECTION_ARGUMENT_SPEC)
    argument_spec["provider"] = dict(required=False, type="dict", options=CONNECTION_ARGUMENT_SPEC)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=MUTUALLY_EXCLUSIVE,
        required_one_of=[REQUIRED_ONE_OF],
        required_if=[["platform", PLATFORM_F5, ["volume"]]],
        supports_check_mode=False,
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

    kwargs = {}
    if ntc_host is not None:
        device = ntc_device_by_name(ntc_host, ntc_conf_file)
    else:
        if transport is not None:
            kwargs["transport"] = transport
        if port is not None:
            kwargs["port"] = port
        if secret is not None:
            kwargs["secret"] = secret

        device_type = platform
        device = ntc_device(device_type, host, username, password, **kwargs)

    confirm = module.params["confirm"]
    timer = module.params["timer"]
    timeout = module.params["timeout"]
    volume = module.params["volume"]

    if not confirm:
        module.fail_json(msg="confirm must be set to true for this module to work.")

    supported_timer_platforms = [PLATFORM_IOS, PLATFORM_JUNOS]

    if timer is not None and device.device_type not in supported_timer_platforms:
        module.fail_json(msg="Timer parameter not supported on platform %s." % platform)

    argument_check = {"host": host, "username": username, "platform": platform, "password": password}

    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    device.open()

    if volume:
        device.reboot(confirm=True, volume=volume)
    elif timer is not None:
        device.reboot(confirm=True, timer=timer)
    else:
        device.reboot(confirm=True)

    time.sleep(10)
    reachable, atomic = check_device(module, username, password, host, timeout, kwargs)

    changed = True
    rebooted = True

    module.exit_json(changed=changed, rebooted=rebooted, reachable=reachable, atomic=atomic)


if __name__ == "__main__":
    main()
