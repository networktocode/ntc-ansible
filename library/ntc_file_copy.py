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
    - Supported platforms: Cisco Nexus switches with NX-API, Cisco IOS switches or routers, Arista switches with eAPI.
Notes:
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
        required: true
        choices: ['cisco_nxos_nxapi', 'arista_eos_eapi', 'cisco_ios']
    local_file:
        description:
            - Path to local file. Local directory must exist.
        required: true
    remote_file:
        description:
            - Remote file path to be copied to flash. Remote directories must exist.
              If omitted, the name of the local file will be used.
        required: false
        default: null
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
            - Transport protocol for API-based devices. Not used for actual file transfer.
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
- ntc_file_copy:
    platform: cisco_nxos_nxapi
    local_file: /path/to/file
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    transport: http

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
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"
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
'''

import os

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
            local_file=dict(required=True),
            remote_file=dict(required=False),
            host=dict(required=True),
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str'),
            secret=dict(required=False),
            transport=dict(default='https', choices=['http', 'https']),
            port=dict(required=False, type='int')
        ),
        supports_check_mode=True
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

    local_file = module.params['local_file']
    remote_file = module.params['remote_file']

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

    changed = False
    transfer_status = 'No Transfer'
    file_exists = True

    if not os.path.isfile(local_file):
        module.fail_json(msg="Local file {} not found".format(local_file))

    if remote_file is not None:
        device.stage_file_copy(local_file, remote_file)
    else:
        device.stage_file_copy(local_file)
        remote_file = os.path.basename(local_file)

    if not device.file_copy_remote_exists():
        changed = True
        file_exists = False

    if not module.check_mode and not file_exists:
        try:
            device.file_copy()
            transfer_status = 'Sent'
        except Exception as e:
            module.fail_json(msg=str(e))

    device.close()

    module.exit_json(changed=changed, transfer_status=transfer_status, local_file=local_file, remote_file=remote_file)

from ansible.module_utils.basic import *
main()
