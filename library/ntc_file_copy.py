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
module: ntc_file_copy
short_description: Copy a file to a remote network device over SCP.
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
options:
    platform:
        description:
            - Switch platform
        required: false
        choices: ['cisco_nxos_nxapi', 'arista_eos_eapi', 'cisco_ios_ssh']
    local_file:
        description:
            - Path to local file. Local directory must exist.
        required: false
    remote_file:
        description:
            - Remote file path of the copy. Remote directories must exist.
              If omitted, the name of the local file will be used.
        required: false
        default: null
    file_system:
        description:
            - The remote file system of the device. If omitted,
              devices that support a file_system parameter will use their default values.
        required: false
        default: null
    host:
        description:
            - Hostame or IP address of switch.
        required: false
    provider:
        description:
          - Dictionary which acts as a collection of arguments used to define the characteristics
            of how to connect to the device.
            Note - host, username, password, local_file, and platform must be defined in either
            provider or local param
            Note - local param takes precedence, e.g. hostname is preferred to provider['host']
        required: false
    username:
        description:
            - Username used to login to the target device
        required: false
    password:
        description:
            - Password used to login to the target device
        required: false
    secret:
        description:
            - Enable secret for devices connecting over SSH.
        required: false
    transport:
        description:
            - Transport protocol for API-based devices. Not used for actual file transfer.
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


- ntc_file_copy:
    platform: cisco_nxos_nxapi
    local_file: /path/to/file
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    transport: http
- ntc_file_copy:
    ntc_host: n9k1
    ntc_conf_file: .ntc.conf
    local_file: /path/to/file
- ntc_file_copy:
    ntc_host: eos_leaf
    local_file: /path/to/file
- ntc_file_copy:
    platform: arista_eos_eapi
    local_file: /path/to/file
    remote_file: /path/to/remote_file
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
- ntc_file_copy:
    platform: cisco_ios
    local_file: "{{ local_file_1 }}"
    provider: "{{ nxos_provider }}"
'''

RETURN = '''
transfer_status:
    description: Whether a file was transfered. "No Transfer" or "Sent".
    returned: success
    type: string
    sample: 'Sent'
local_file:
    description: The path of the local file.
    returned: success
    type: string
    sample: '/path/to/local/file'
remote_file:
    description: The path of the remote file.
    returned: success
    type: string
    sample: '/path/to/remote/file'
atomic:
    description: Whether the module has atomically completed all steps,
                 including closing connection after file delivering.
    returned: always
    type: boolean
    sample: true
'''

import os

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
            local_file=dict(required=False),
            remote_file=dict(required=False),
            file_system=dict(required=False),
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
        supports_check_mode=True
    )

    provider = module.params['provider'] or {}

    no_log = ['password', 'secret']
    for param in no_log:
        if provider.get(param):
            module.no_log_values.update(return_values(provider[param]))

    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) != False:
            module.params[param] = module.params.get(param) or pvalue


    if not HAS_PYNTC:
        module.fail_json(msg='pyntc Python library not found.')

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

    local_file = module.params['local_file']
    remote_file = module.params['remote_file']
    file_system = module.params['file_system']


    argument_check = { 'host': host, 'username': username, 'platform': platform, 'password': password, 'local_file': local_file }
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    device.open()

    changed = False
    transfer_status = 'No Transfer'
    file_exists = True

    if not os.path.isfile(local_file):
        module.fail_json(msg="Local file {} not found".format(local_file))

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

            transfer_status = 'Sent'
        except Exception as e:
            module.fail_json(msg=str(e))

    try:
        device.close()
        atomic = True
    except:
        atomic = False

    if remote_file is None:
        remote_file = os.path.basename(local_file)

    module.exit_json(changed=changed, transfer_status=transfer_status,
                     local_file=local_file, remote_file=remote_file,
                     file_system=file_system, atomic=atomic)

from ansible.module_utils.basic import *
main()
