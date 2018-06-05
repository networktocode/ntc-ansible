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
    - Supported platforms include Cisco Nexus switches with NX-API, Cisco IOS switches or routers, Arista switches with eAPI.
notes:
    - Facts to be returned include - uptime (string), uptime (seconds), model, vendor, os_version, serial_number, hostname, fqdn, vlans, interfaces.
    - Facts are automatically added to Ansible facts environment. No need to register them.
author: Jason Edelman (@jedelman8)
version_added: 1.9.2
requirements:
    - pyntc
options:
    platform:
        description:
            - Switch platform
        required: false
        default: null
        choices: ['cisco_nxos_nxapi', 'arista_eos_eapi', 'cisco_ios_ssh']
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
'''

EXAMPLES = '''
vars:
  nxos_provider:
    host: "{{ inventory_hostname }}"
    username: "ntc-ansible"
    password: "ntc-ansible"
    platform: "cisco_nxos"
    connection: ssh

- ntc_get_facts:
    provider: "{{ nxos_provider }}"
    ntc_host: n9k1
    ntc_conf_file: .ntc.conf

- ntc_get_facts:
    platform: cisco_nxos_nxapi
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    transport: http

- ntc_get_facts:
    ntc_host: n9k1
    ntc_conf_file: .ntc.conf

- ntc_get_facts:
    ntc_host: eos_leaf

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
uptime_string:
    description: The device uptime represented as a string format DD:HH:MM:SS.
    returned: success
    type: string
    sample: "00:00:21:53"
uptime:
    description: The device uptime represented as an integer number of strings.
    returned: success
    type: int
    sample: 1313
vlans:
    description: List of VLAN IDs.
    returned: success
    type: List
    sample: [
            "1",
            "2",
            "3",
            "4",
        ]
vendor:
    description: Vendor of network device.
    returned: success
    type: string
    sample: "cisco"
os_version:
    description: Operating System version on network device.
    returned: success
    type: string
    sample: "7.0(3)I2(1)"
serial_number:
    description: Serial number on network device.
    returned: success
    type: string
    sample: "SAL1819S6LU"
model:
    description: Hardware model of network device.
    returned: success
    type: string
    sample: "Nexus9000 C9396PX Chassis"
hostname:
    description: Hostname of network device.
    returned: success
    type: string
    sample: "N9K1"
fqdn:
    description: Fully-qualified domain name.
    returned: success
    type: string
    sample: "N9K1.ntc.com"
interfaces:
    description: List of interfaces.
    returned: success
    type: list
    sample: [
            "mgmt0",
            "Ethernet1/1",
            "Ethernet1/2",
            "Ethernet1/3",
            "Ethernet1/4",
            "Ethernet1/5",
            "Ethernet1/6",
    ]
'''

try:
    HAS_PYNTC = True
    from pyntc import ntc_device, ntc_device_by_name
except ImportError:
    HAS_PYNTC = False

PLATFORM_NXAPI = 'cisco_nxos_nxapi'
PLATFORM_IOS = 'cisco_ios_ssh'
PLATFORM_EAPI = 'arista_eos_eapi'
PLATFORM_JUNOS = 'juniper_junos_netconf'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            platform=dict(choices=[PLATFORM_NXAPI, PLATFORM_IOS, PLATFORM_EAPI, PLATFORM_JUNOS],
                          required=False),
            host=dict(required=False),
            username=dict(required=False, type='str'),
            password=dict(required=False, type='str', no_log=True),
            secret=dict(required=False, no_log=True),
            transport=dict(required=False, choices=['http', 'https']),
            port=dict(required=False, type='int'),
            provider=dict(type='dict', required=False),
            ntc_host=dict(required=False),
            ntc_conf_file=dict(required=False),
        ),
        mutually_exclusive=[['host', 'ntc_host'],
                            ['ntc_host', 'secret'],
                            ['ntc_host', 'transport'],
                            ['ntc_host', 'port'],
                            ['ntc_conf_file', 'secret'],
                            ['ntc_conf_file', 'transport'],
                            ['ntc_conf_file', 'port'],
                           ],
        required_one_of=[['host', 'ntc_host', 'provider']],
        supports_check_mode=False
    )

    if not HAS_PYNTC:
        module.fail_json(msg='pyntc Python library not found.')

    provider = module.params['provider'] or {}

    no_log = ['password', 'secret']
    for param in no_log:
        if provider.get(param):
            module.no_log_values.update(return_values(provider[param]))

    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) != False:
            module.params[param] = module.params.get(param) or pvalue

    platform = module.params['platform']
    host = module.params['host']
    username = module.params['username']
    password = module.params['password']

    ntc_host = module.params['ntc_host']
    ntc_conf_file = module.params['ntc_conf_file']

    transport = module.params['transport']
    port = module.params['port']
    secret = module.params['secret']

    argument_check = { 'host': host, 'username': username, 'platform': platform, 'password': password }
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    if ntc_host is not None:
        device = ntc_device_by_name(ntc_host, ntc_conf_file)
    else:
        kwargs = {}
        if transport is not None:
            kwargs['transport'] = transport
        if port is not None:
            kwargs['port'] = port
        if secret is not None:
            kwargs['secret'] = secret

        device_type = platform
        device = ntc_device(device_type, host, username, password, **kwargs)

    device.open()
    facts = device.facts
    device.close()

    module.exit_json(ansible_facts=facts)

from ansible.module_utils.basic import *
main()
