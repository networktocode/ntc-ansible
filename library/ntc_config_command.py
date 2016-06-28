#!/usr/bin/env python

# Copyright 2015 James Williams <james.williams@packetgeek.net>
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
module: ntc_config_command
short_description: Writes config data to devices that don't have an API
description:
    - This module write config data to devices that don't have an API.
      The use case would be writing configuration based on output gleaned
      from ntc_show_command output.
author: James Williams (@packetgeeknet)
requirements:
    - netmiko
options:
    connection:
        description:
            - connect to device using netmiko or read from offline file
              for testing
        required: false
        default: ssh
        choices: ['ssh']
        aliases: []
    platform:
        description:
            - Platform FROM the index file
        required: true
        default: ssh
        choices: []
        aliases: []
    commands:
        description:
            - Command to execute on target device
        required: false
        default: null
        choices: []
        aliases: []
    commands_file:
        description:
            - Command to execute on target device
        required: true
        default: null
        choices: []
    host:
        description:
            - IP Address or hostname (resolvable by Ansible control host)
        required: false
        default: null
        choices: []
        aliases: []
    port:
        description:
            - SSH port to use to connect to the target device
        required: false
        default: 22
        choices: []
        aliases: []
    username:
        description:
            - Username used to login to the target device
        required: false
        default: null
        choices: []
        aliases: []
    password:
        description:
            - Password used to login to the target device
        required: false
        default: null
        choices: []
        aliases: []
    secret:
        description:
            - Password used to enter a privileged mode on the target device
        required: false
        default: null
        choices: []
        aliases: []
    use_keys:
        description:
            - Boolean true/false if ssh key login should be attempted
        required: false
        default: false
    key_file:
        description:
            - Path to private ssh key used for login
        required: false
        default: null
'''

EXAMPLES = '''

# write vlan data
- ntc_config_command:
    connection: ssh
    platform: cisco_nxos
    commands:
      - vlan 10
      - name vlan_10
      - end
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"

# write config from file
- ntc_config_command:
    connection: ssh
    platform: cisco_nxos
    commands_file: "dynamically_created_config.txt"
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"
'''

import os.path
import socket
from netmiko import ConnectHandler


def error_params(platform, command_output):
    if 'cisco_ios' in platform:
        if "Invalid input detected at '^' marker" in command_output:
            return True
        elif "Ambiguous command" in command_output:
            return True
        else:
            return False


def main():

    module = AnsibleModule(
        argument_spec=dict(
            connection=dict(choices=['ssh'],
                            default='ssh'),
            platform=dict(required=True),
            commands=dict(required=False, type='list'),
            commands_file=dict(required=False),
            host=dict(required=False),
            port=dict(default=22, required=False),
            username=dict(required=False, type='str'),
            password=dict(required=False, type='str'),
            secret=dict(required=False, type='str'),
            use_keys=dict(required=False, default=False, type='bool'),
            key_file=dict(required=False, default=None, type='str'),
        ),
        required_together=(
            ['host', 'password', 'username'],
        ),
        supports_check_mode=False
    )

    connection = module.params['connection']
    platform = module.params['platform']
    device_type = platform.split('-')[0]
    commands = module.params['commands']
    commands_file = module.params['commands_file']
    username = module.params['username']
    password = module.params['password']
    secret = module.params['secret']
    use_keys = module.params['use_keys']
    key_file = module.params['key_file']
    port = int(module.params['port'])

    if module.params['host']:
        host = socket.gethostbyname(module.params['host'])

    if connection == 'ssh' and not module.params['host']:
        module.fail_json(msg='specify host if using connection=ssh')

    if connection == 'ssh':

        device = ConnectHandler(device_type=device_type,
                                ip=socket.gethostbyname(host),
                                port=port,
                                username=username,
                                password=password,
                                secret=secret,
                                use_keys=use_keys,
                                key_file=key_file
                                )

        if secret:
            device.enable()

        if commands:
            output = device.send_config_set(commands)

        try:
            if commands_file:
                if os.path.isfile(commands_file):
                    with open(commands_file, 'r') as f:
                        output = device.send_config_set(f.readlines())
        except:
            module.fail_json(msg="Unable to locate: {}".format(commands_file))

    if (error_params(platform, output)):
        module.fail_json(msg="Error executing command:\
                         {}".format(output))

    results = {}
    results['response'] = output

    module.exit_json(changed=True, **results)


from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
