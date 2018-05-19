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
module: ntc_rollback
short_description: Set a checkpoint or rollback to a checkpoint
description:
    - This module offers the ability to set a configuration checkpoint file or rollback
      to a configuration checkpoint file on supported Cisco or Arista switches.
    - Supported platforms include Cisco Nexus switches with NX-API, Cisco IOS switches or routers, Arista switches with eAPI.
notes:
    - This module is not idempotent.
author: Jason Edelman (@jedelman8)
requirements:
    - pyntc
options:
    platform:
        description:
            - Vendor and platform identifier.
        required: false
        choices: ['cisco_nxos_nxapi', 'cisco_ios_ssh', 'arista_eos_eapi']
    checkpoint_file:
        description:
            - Name of checkpoint file to create. Mutually exclusive with rollback_to.
        required: false
        default: null
    rollback_to:
        description:
            - Name of checkpoint file to rollback to. Mutually exclusive with checkpoint_file.
        required: false
        default: null
    host:
        description:
            - Hostame or IP address of switch.
        required: false
    username:
        description:
            - Username used to login to the target device.
        required: false
    password:
        description:
            - Password used to login to the target device.
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
            - Transport protocol for API. Only needed for NX-API and eAPI.
              If omitted, platform-specific default will be used.
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

- ntc_rollback:
    provider: "{{ nxos_provider }}"
    rollback_to: backup.cfg

- ntc_rollback:
    ntc_host: eos1
    checkpoint_file: backup.cfg

- ntc_rollback:
    ntc_host: eos1
    rollback_to: backup.cfg
'''

RETURN = '''
filename:
    description: The filename of the checkpoint/rollback file.
    returned: success
    type: string
    sample: 'backup.cfg'
status:
    description: Which operation took place and whether it was successful.
    returned: success
    type: string
    sample: 'rollback executed'
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
            provider=dict(required=False, type='dict'),
            password=dict(required=False, type='str', no_log=True),
            secret=dict(required=False, no_log=True),
            transport=dict(required=False, choices=['http', 'https']),
            port=dict(required=False, type='int'),
            ntc_host=dict(required=False),
            ntc_conf_file=dict(required=False),
            checkpoint_file=dict(required=False),
            rollback_to=dict(required=False),
        ),
        mutually_exclusive=[['host', 'ntc_host'],
                            ['ntc_host', 'secret'],
                            ['ntc_host', 'transport'],
                            ['ntc_host', 'port'],
                            ['ntc_conf_file', 'secret'],
                            ['ntc_conf_file', 'transport'],
                            ['ntc_conf_file', 'port'],
                            ['checkpoint_file', 'rollback_to'],
                           ],
        required_one_of=[['host', 'ntc_host', 'provider']],
        required_together=[['host', 'username', 'password', 'platform']],
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

    checkpoint_file = module.params['checkpoint_file']
    rollback_to = module.params['rollback_to']

    argument_check = { 'host': host, 'username': username, 'platform': platform, 'password': password }
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
            status = 'checkpoint file created'
        elif rollback_to:
            device.rollback(rollback_to)
            status = 'rollback executed'
        changed = True
        filename = rollback_to or checkpoint_file
    except Exception as e:
        module.fail_json(msg=str(e))

    device.close()
    module.exit_json(changed=changed, status=status, filename=filename)

from ansible.module_utils.basic import *
main()
