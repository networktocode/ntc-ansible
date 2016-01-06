#!/usr/bin/env python

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

DOCUMENTATION = '''
---
module: ntc_get_facts
short_description: Get facts about a remote network device.
description:
    - Reboot a network device, optionally on a timer.
    - Supported platforms: Cisco Nexus switches with NX-API, Cisco IOS switches or routers, Arista switches with eAPI.
notes:
    - Facts to be returned:
        - uptime (string)
        - uptime (seconds)
        - model
        - vendor
        - os_version
        - serial_number
        - hostname
        - fqdn
        - vlans
        - interfaces
author: Jason Edelman (@jedelman8)
version_added: 1.9.2
requirements:
    - pyntc
options:
    platform:
        description:
            - Switch platform
        required: true
        choices: ['cisco_nxos_nxapi', 'arista_eos_eapi', 'cisco_ios']
    host:
        description:
            - Hostame or IP address of switch.
        required: true
    username:
        description:
            - Username used to login to the target device
        required: true
    password:
        description:
            - Password used to login to the target device
        required: true
    secret:
        description:
            - Enable secret for devices connecting over SSH.
        required: false
    transport:
        description:
            - Transport protocol for API-based devices.
        required: false
        default: https
        choices: ['http', 'https']
    port:
        description:
            - TCP/UDP port to connect to target device. If omitted standard port numbers will be used.
              80 for HTTP; 443 for HTTPS; 22 for SSH.
        required: false
        default: null
'''

EXAMPLES = '''
- ntc_get_facts:
    platform: cisco_nxos_nxapi
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    transport: http

- ntc_get_facts:
    platform: arista_eos_eapi
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"

- ntc_get_facts:
    platform: cisco_ios
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"
'''

RETURN = '''
facts:
    description: Dictionary of facts
    returned: success
    type: dictionary
    sample: {
    "uptime_string": "00:00:21:53",
    "uptime": 1313,
    "vlans": [
        "1",
        "2",
        "3",
        "4",
    ],
    "vendor": "cisco",
    "os_version": "7.0(3)I2(1)",
    "serial_number": "SAL1819S6LU",
    "model": "Nexus9000 C9396PX Chassis",
    "hostname": "N9K1",
    "fqdn": "N/A"
    "interfaces": [
        "mgmt0",
        "Ethernet1/1",
        "Ethernet1/2",
        "Ethernet1/3",
        "Ethernet1/4",
        "Ethernet1/5",
        "Ethernet1/6",
    ]
}
'''

try:
    HAS_PYNTC = True
    from pyntc import ntc_device
except ImportError:
    HAS_PYNTC = False

PLATFORM_NXAPI = 'cisco_nxos_nxapi'
PLATFORM_IOS = 'cisco_ios'
PLATFORM_EAPI = 'arista_eos_eapi'

platform_to_device_type = {
    PLATFORM_EAPI: 'eos',
    PLATFORM_NXAPI: 'nxos',
    PLATFORM_IOS: 'ios',
}

def main():
    module = AnsibleModule(
        argument_spec=dict(
            platform=dict(choices=[PLATFORM_NXAPI, PLATFORM_IOS, PLATFORM_EAPI],
                          required=True),
            host=dict(required=True),
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str'),
            secret=dict(required=False),
            transport=dict(default='https', choices=['http', 'https']),
            port=dict(required=False, type='int')
        ),
        supports_check_mode=False
    )

    if not HAS_PYNTC:
        module.fail_json(msg='pyntc Python library not found.')

    platform = module.params['platform']
    host = module.params['host']
    username = module.params['username']
    password = module.params['password']

    transport = module.params['transport']
    port = module.params['port']
    secret = module.params['secret']

    kwargs = {}
    if transport is not None:
        kwargs['transport'] = transport
    if port is not None:
        kwargs['port'] = port
    if secret is not None:
        kwargs['secret'] = secret

    device_type = platform_to_device_type[platform]
    device = ntc_device(device_type, host, username, password, **kwargs)

    device.open()
    facts = device.facts
    device.close()

    module.exit_json(facts=facts)

from ansible.module_utils.basic import *
main()
