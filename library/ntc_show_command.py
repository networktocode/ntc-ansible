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
module: ntc_show_command
short_description: Gets output from show commands using SSH and tries to return structured data
description:
    - This module connects to network devices using SSH and tries to
      return structured data (JSON) using TextFSM templates. If a template
      is not found, raw text is returned.  This module supports two drivers,
      namely netmiko/SSH and trigger/SSH. Device support is dependent on
      netmiko and trigger.  The ability to return structured data is dependent
      on TextFSM templates.  You can still pass in optional param to the
      Trigger Commando init using the optional args param which is a
      dictionary. Many other params can be defined in the Trigger netdevices
      file when using trigger/SSH. Currently, this module requires passing in
      un/pwd even when a Trigger .tacacsrc file exists.
author: Jason Edelman (@jedelman8)
requirements:
    - netmiko
    - textfsm
    - terminal
    - trigger
options:
    connection:
        description:
            - connect to device using netmiko or read from offline file
              for testing.  ssh is the same as netmiko_ssh.
        required: false
        default: ssh
        choices: ['ssh', 'offline', 'netmiko_ssh', 'trigger_ssh']
        aliases: []
    platform:
        description:
            - Platform FROM the index file
        required: true
        default: ssh
        choices: []
        aliases: []
    template_dir:
        description:
            - path where TextFSM templates are stored. Default path is ntc
              with ntc in the same working dir as the playbook being run
        required: false
        default: ntc_templates
        choices: []
        aliases: []
    index_file:
        description:
            - name of index file.  file location must be relative to
              the template_dir
        required: false
        default: index
        choices: []
        aliases: []
    use_templates:
        description:
            - Boolean true/false to enable/disable use of TextFSM templates for parsing
        required: false
        default: true
        choices: ['true', 'false', 'yes', 'no']
        aliases: []
    local_file:
        description:
            - Specify local file to save raw output to
        required: false
        default: null
        choices: []
        aliases: []
    file:
        description:
            - If using connection=offline, this is the file (with path)
              of a file that contains raw text output, i.e.
              'show command' and then the contents of the file will
              be rendered with the the TextFSM template
        required: false
        default: null
        choices: []
        aliases: []
    command:
        description:
            - Command to execute on target device
        required: true
        default: null
        choices: []
        aliases: []
    host:
        description:
            - IP Address or hostname (resolvable by Ansible control host)
        required: false
        default: null
        choices: []
        aliases: []
    port:
        description:
            - SSH port to use to connect to the target device when using netmiko
        required: false
        default: 22
        choices: []
        aliases: []
    delay:
        description:
            - Wait for command output from target device when using netmiko
        required: false
        default: 1
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
            - Password used to enter a privileged mode on the target device when using netmiko
        required: false
        default: null
        choices: []
        aliases: []
    use_keys:
        description:
            - Boolean true/false if ssh key login should be attempted when nsing netmiko
        required: false
        default: false
        choices: []
        aliases: []
    key_file:
        description:
            - Path to private ssh key used for login when using netmiko
        required: false
        default: null
        choices: []
        aliases: []
'''
EXAMPLES = '''

# get vlan data using netmiko
- ntc_show_command:
    connection=ssh
    platform=cisco_nxos
    command='show vlan'
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}

# get snmp community using netmiko
- ntc_show_command:
    connection=ssh
    platform=cisco_nxos
    command='show snmp community'
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
    secret:{{ secret }}

# FEEDING SINGLE DEVICE TO TRIGGER USING HOST PARAM
-  ntc_show_command:
    connection: trigger_ssh
    host: "{{ inventory_hostname }}"
    platform: cisco_nxos
    command: 'show version'
    username: "{{ username }}"
    password: "{{ password }}"

# FEEDING SINGLE DEVICE TO TRIGGER USING LIST
-  ntc_show_command:
    connection: trigger_ssh
    trigger_device_list:
      - "{{ inventory_hostname }}"
    platform: cisco_nxos
    command: 'show version'
    username: "{{ username }}"
    password: "{{ password }}"

# FEEDING LIST OF DEVICES TO TRIGGER
- ntc_show_command:
    connection: trigger_ssh
    trigger_device_list:
      - n9k1
      - n9k2
    platform: cisco_nxos
    command: 'show version'
    username: "{{ username }}"
    password: "{{ password }}"
  run_once: true

# FEEDING SINGLE DEVICE TO NETIMKO
-  ntc_show_command:
    connection: netmiko_ssh
    platform: cisco_nxos
    command: 'show version'
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"

'''

import os.path
import socket

HAS_NETMIKO = True
try:
    from netmiko import ConnectHandler
except:
    HAS_NETMIKO = False

HAS_TEXTFSM = True
try:
    from clitable import CliTableError
    import clitable
except:
    try:
        from textfsm.clitable import CliTableError
        import textfsm.clitable as clitable
    except:
        HAS_TEXTFSM = False

HAS_TRIGGER = True
try:
    from trigger.cmds import Commando
except:
    HAS_TRIGGER = False


def clitable_to_dict(cli_table):
    """Converts TextFSM cli_table object to list of dictionaries
    """
    objs = []
    for row in cli_table:
        temp_dict = {}
        for index, element in enumerate(row):
            temp_dict[cli_table.header[index].lower()] = element
        objs.append(temp_dict)

    return objs


def get_structured_data(rawoutput, module):
    index_file = module.params['index_file']
    template_dir = module.params['template_dir']
    cli_table = clitable.CliTable(index_file, template_dir)

    attrs = dict(
        Command=module.params['command'],
        Platform=module.params['platform']
    )
    try:
        cli_table.ParseCmd(rawoutput, attrs)
        structured_data = clitable_to_dict(cli_table)
    except CliTableError as e:
        # Invalid or Missing template
        # module.fail_json(msg='parsing error', error=str(e))
        # rather than fail, fallback to return raw text
        structured_data = [rawoutput]

    return structured_data


def parse_raw_output(rawoutput, module):
    """Returns a dict if using netmiko and list of dicts if using trigger
    """
    structured_data_response_list = []
    structured_data = {}
    if isinstance(rawoutput, dict):
        for device, command_output in rawoutput.items():

            raw_txt = command_output[module.params['command']]
            sd = get_structured_data(raw_txt, module)
            temp = dict(device=device, response=sd)
            structured_data_response_list.append(temp)
    else:
        structured_data = get_structured_data(rawoutput, module)

    return structured_data or structured_data_response_list


def main():

    module = AnsibleModule(
        argument_spec=dict(
            connection=dict(choices=['ssh', 'offline', 'netmiko_ssh',
                            'trigger_ssh'], default='netmiko_ssh'),
            platform=dict(required=True),
            file=dict(required=False),
            local_file=dict(required=False),
            index_file=dict(default='index'),
            template_dir=dict(default='ntc-templates/templates'),
            use_templates=dict(required=False, default=True, type='bool'),
            trigger_device_list=dict(type='list', required=False),
            command=dict(required=True),
            host=dict(required=False),
            port=dict(default=22, required=False),
            delay=dict(default=1, required=False),
            username=dict(required=False, type='str'),
            password=dict(required=False, type='str'),
            secret=dict(required=False, type='str'),
            use_keys=dict(required=False, default=False, type='bool'),
            key_file=dict(required=False, default=None),
            optional_args=dict(required=False, type='dict', default={}),
        ),
        required_together=(
            ['password', 'username'],
        ),
        mutually_exclusive=(
            ['host', 'trigger_device_list'],
        ),
        supports_check_mode=False
    )

    if not HAS_TEXTFSM:
        module.fail_json(msg='This module requires TextFSM')

    connection = module.params['connection']
    platform = module.params['platform']
    device_type = platform.split('-')[0]
    raw_file = module.params['file']
    local_file = module.params['local_file']
    index_file = module.params['index_file']
    template_dir = module.params['template_dir']
    command = module.params['command']
    username = module.params['username']
    password = module.params['password']
    secret = module.params['secret']
    use_templates = module.params['use_templates']
    use_keys = module.params['use_keys']
    key_file = module.params['key_file']
    port = int(module.params['port'])
    delay = int(module.params['delay'])
    trigger_device_list = module.params['trigger_device_list']
    optional_args = module.params['optional_args']
    host = module.params['host']

    if connection in ['ssh', 'netmiko_ssh'] and not module.params['host']:
        module.fail_json(msg='specify host when connection=ssh/netmiko_ssh')

    if connection != 'offline':
        if not host and not trigger_device_list:
            module.fail_json(msg='specify host or trigger_device_list based on connection')

    if connection == 'offline' and not raw_file:
        module.fail_json(msg='specifiy file if using connection=offline')

    if template_dir.endswith('/'):
        template_dir.rstrip('/')

    if use_templates:
        if not os.path.isfile(template_dir + '/' + index_file):
            module.fail_json(msg='could not find or read index file')

        if raw_file and not os.path.isfile(raw_file):
            module.fail_json(msg='could not read raw text file')

    rawtxt = ''
    if connection in ['ssh', 'netmiko_ssh']:
        if not HAS_NETMIKO:
            module.fail_json(msg='This module requires netmiko.')

        device = ConnectHandler(
            device_type=device_type,
            ip=host,
            port=port,
            username=username,
            password=password,
            secret=secret,
            use_keys=use_keys,
            key_file=key_file
        )
        if secret:
            device.enable()

        rawtxt = device.send_command_expect(command, delay_factor=delay)

    elif connection == 'trigger_ssh':
        if not HAS_TRIGGER:
            module.fail_json(msg='This module requires trigger.')
        kwargs = {}
        kwargs['production_only'] = False
        kwargs['force_cli'] = True
        if optional_args:
            kwargs.update(optional_args)

        if host:
            commando = Commando(devices=[host], commands=[command],
                                creds=(username, password), **kwargs)
            commando.run()
            rawtxt = commando.results[host][command]
        elif trigger_device_list:
            commando = Commando(devices=trigger_device_list, commands=[command],
                                creds=(username, password), **kwargs)
            commando.run()

    elif connection == 'offline':
        with open(raw_file, 'r') as data:
            rawtxt = data.read()

    if local_file:
        with open(local_file, 'w') as f:
            f.write(rawtxt)

    results = {}
    results['response'] = []
    results['response_list'] = []

    if use_templates:
        if rawtxt:
            results['response'] = parse_raw_output(rawtxt, module)
        elif trigger_device_list:
            results['response_list'] = parse_raw_output(commando.results, module)
    elif rawtxt:
        results['response'] = [rawtxt]
    elif trigger_device_list:
        results['response'] = [commando.results]

    module.exit_json(**results)


from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
