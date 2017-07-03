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
module: ntc_reboot
short_description: Reboot a network device.
description:
    - Reboot a network device, optionally on a timer.
    - Supported platforms include Cisco Nexus switches with NX-API, Cisco IOS switches or routers, Arista switches with eAPI.
Notes:
    - The timer is only supported for IOS devices.
author: Jason Edelman (@jedelman8)
version_added: 1.9.2
requirements:
    - pyntc
options:
    platform:
        description:
            - Switch platform
        required: false
        choices: ['cisco_nxos_nxapi', 'arista_eos_eapi', 'cisco_ios_ssh']
    timer:
        description:
            - Time in minutes after which the device will be rebooted.
        required: false
        default: null
    timeout:
        description:
            - Time in seconds to wait for the device and API to come back up.
              Uses specified port/protocol as defined with port and protocol params.
        required: false
        default: 240
    confirm:
        description:
            - Safeguard boolean. Set to true if you're sure you want to reboot.
        required: false
        default: false
    host:
        description:
            - Hostame or IP address of switch.
        required: false
    username:
        description:
            - Username used to login to the target device
        required: false
    password:
        description:
            - Password used to login to the target device
        required: false
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
    platform: cisco_nxos_nxapi
    connection: http

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
'''

RETURN = '''
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
'''

import time

try:
    HAS_PYNTC = True
    from pyntc import ntc_device, ntc_device_by_name
except ImportError:
    HAS_PYNTC = False

PLATFORM_NXAPI = 'cisco_nxos_nxapi'
PLATFORM_IOS = 'cisco_ios_ssh'
PLATFORM_EAPI = 'arista_eos_eapi'
PLATFORM_JUNOS = 'juniper_junos_netconf'


def check_device(module, username, password, host, timeout, kwargs):
    success = False
    attempts = timeout / 30
    counter = 0
    atomic = False
    while counter < attempts and not success:
        try:
            if module.params['ntc_host'] is not None:
                device = ntc_device_by_name(module.params['ntc_host'],
                                            module.params['ntc_conf_file'])
            else:
                device_type = module.params['platform']
                device = ntc_device(device_type, host, username, password, **kwargs)
            success = True
            atomic = True
            try:
                device.close()
            except:
                atomic = False
                pass
        except:
            time.sleep(30)
            counter += 1
    return success, atomic


def main():
    module = AnsibleModule(
        argument_spec=dict(
            platform=dict(choices=[PLATFORM_NXAPI, PLATFORM_IOS, PLATFORM_EAPI, PLATFORM_JUNOS],
                          required=False),
            host=dict(required=False),
            username=dict(required=False, type='str'),
            provider=dict(required=False, type='dict'),
            password=dict(required=False, type='str', no_log=True),
            secret=dict(required=False, no_log=True),
            transport=dict(required=False, choices=['http', 'https']),
            port=dict(required=False, type='int'),
            ntc_host=dict(required=False),
            ntc_conf_file=dict(required=False),
            confirm=dict(required=False, default=False, type='bool', choices=BOOLEANS),
            timer=dict(requred=False, type='int'),
            timeout=dict(required=False, type='int', default=240)
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

    kwargs = {}
    if ntc_host is not None:
        device = ntc_device_by_name(ntc_host, ntc_conf_file)
    else:
        if transport is not None:
            kwargs['transport'] = transport
        if port is not None:
            kwargs['port'] = port
        if secret is not None:
            kwargs['secret'] = secret

        device_type = platform
        device = ntc_device(device_type, host, username, password, **kwargs)

    confirm = module.params['confirm']
    timer = module.params['timer']
    timeout = module.params['timeout']

    if not confirm:
        module.fail_json(msg='confirm must be set to true for this module to work.')

    supported_timer_platforms = [PLATFORM_IOS, PLATFORM_JUNOS]

    if timer is not None \
            and device.device_type not in supported_timer_platforms:
        module.fail_json(msg='Timer parameter not supported on platform %s.' % platform)

    argument_check = { 'host': host, 'username': username, 'platform': platform, 'password': password }
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")
    device.open()

    changed = False
    rebooted = False

    if timer is not None:
        device.reboot(confirm=True, timer=timer)
    else:
        device.reboot(confirm=True)

    time.sleep(10)
    reachable, atomic = check_device(module, username, password, host, timeout, kwargs)

    changed = True
    rebooted = True

    module.exit_json(changed=changed, rebooted=rebooted, reachable=reachable, atomic=atomic)

from ansible.module_utils.basic import *
main()
