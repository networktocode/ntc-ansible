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
        choices: ['ssh', 'telnet']
    platform:
        description:
            - Platform FROM the index file
        required: false
    commands:
        description:
            - Command to execute on target device
        required: false
        default: null
    commands_file:
        description:
            - Command to execute on target device
        required: false
    host:
        description:
            - IP Address or hostname (resolvable by Ansible control host)
        required: false
    provider:
        description:
          - Dictionary which acts as a collection of arguments used to define the characteristics
            of how to connect to the device.
            Note - host, username, password and platform must be defined in either provider
            or local param
            Note - local param takes precedence, e.g. hostname is preferred to provider['host']
        required: false
    port:
        description:
            - SSH port to use to connect to the target device
        required: false
        default: 22 for SSH. 23 for Telnet
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
    secret:
        description:
            - Password used to enter a privileged mode on the target device
        required: false
        default: null
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

vars:
  nxos_provider:
    host: "{{ inventory_hostname }}"
    username: "ntc-ansible"
    password: "ntc-ansible"
    platform: "cisco_nxos"
    connection: ssh

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

- ntc_config_command:
    commands:
      - vlan 10
      - name vlan_10
      - end
    provider: "{{ nxos_provider }}"

'''

import os.path
import socket
try:
    from netmiko import ConnectHandler
    HAS_NETMIKO=True
except ImportError:
    HAS_NETMIKO=False


from ansible import __version__ as ansible_version
if float(".".join(ansible_version.split(".", 2)[:2])) < 2.4:
    raise ImportError("Ansible versions < 2.4 are not supported")


def error_params(platform, command_output):
    if 'cisco_ios' in platform:
        if "Invalid input detected at '^' marker" in command_output:
            return True
        elif "Ambiguous command" in command_output:
            return True
        else:
            return False


def main():
    connection_argument_spec = dict(
        connection=dict(
            choices=[
                'ssh',
                'telnet'
            ],
            default='ssh',
        ),
        platform=dict(required=False, default="cisco_ios"),
        host=dict(required=False),
        port=dict(required=False),
        username=dict(required=False, type='str'),
        password=dict(required=False, type='str', no_log=True),
        secret=dict(required=False, type='str', no_log=True),
        use_keys=dict(required=False, default=False, type='bool'),
        key_file=dict(required=False, default=None),
    )
    base_argument_spec = dict(
        commands=dict(required=False, type='list'),
        commands_file=dict(required=False),
    )
    argument_spec = base_argument_spec
    argument_spec.update(connection_argument_spec)
    argument_spec["provider"] = dict(required=False, type="dict", options=connection_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )

    provider = module.params['provider'] or {}

    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) != False:
            module.params[param] = module.params.get(param) or pvalue

    if not HAS_NETMIKO:
        module.fail_json(msg="This module requires netmiko")

    host = module.params['host']
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


    argument_check = { 'host': host, 'username': username, 'platform': platform, 'password': password }
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    if module.params['host']:
        host = socket.gethostbyname(module.params['host'])

    if connection == 'telnet' and platform != 'cisco_ios':
        module.fail_json(msg='only cisco_ios supports '
                             'telnet connection')

    if platform == 'cisco_ios' and connection == 'telnet':
        device_type = 'cisco_ios_telnet'

    if module.params['port']:
        port = int(module.params['port'])
    else:
        if connection == 'telnet':
            port = 23
        else:
            port = 22

    if connection in ['ssh', 'telnet']:
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
        else:
            try:
                if commands_file:
                    if os.path.isfile(commands_file):
                        with open(commands_file, 'r') as f:
                            output = device.send_config_set(f.readlines())
            except IOError:
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
