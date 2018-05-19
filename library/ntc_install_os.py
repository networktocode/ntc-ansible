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
module: ntc_install_os
short_description: Install an operating system by setting the boot options like boot image and kickstart image.
description:
    - Set boot options like boot image and kickstart image.
    - Supported platforms include Cisco Nexus switches with NX-API, Cisco IOS switches or routers, Arista switches with eAPI.
notes:
    - Do not include full file paths, just the name of the file(s) stored on the top level flash directory.
    - You must know if your platform supports taking a kickstart image as a parameter. If supplied but not supported, errors may occur.
    - It may be useful to use this module in conjuction with ntc_file_copy and ntc_reboot.
    - With NXOS devices, this module attempts to install the software immediately, wich may trigger a reboot.
    - With NXOS devices, install process may take up to 10 minutes, especially if the device reboots.
    - Tested on Nexus 3000, 5000, 9000.
    - In check mode, the module tells you if the current boot images are set to the desired images.
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
    system_image_file:
        description:
            - Name of the system (or combined) image file on flash.
        required: true
    kickstart_image_file:
        description:
            - Name of the kickstart image file on flash.
        required: false
        default: null
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
  ios_provider:
    host: "{{ inventory_hostname }}"
    username: "ntc-ansible"
    password: "ntc-ansible"
    platform: "cisco_ios_ssh"
    connection: ssh

- ntc_install_os:
    ntc_host: n9k1
    system_image_file: n9000-dk9.6.1.2.I3.1.bin

- ntc_install_os:
    ntc_host: n3k1
    system_image_file: n3000-uk9.6.0.2.U6.5.bin
    kickstart_image_file: n3000-uk9-kickstart.6.0.2.U6.5.bin

- ntc_install_os:
    ntc_host: c2801
    system_image_file: c2800nm-adventerprisek9_ivs_li-mz.151-3.T4.bin

- ntc_install_os:
    provider: "{{ ios_provider }}"
    system_image_file: c2800nm-adventerprisek9_ivs_li-mz.151-3.T4.bin
'''

RETURN = '''
install_state:
    returned: always
    type: dictionary
    sample: {
        "kick": "n5000-uk9-kickstart.7.2.1.N1.1.bin",
        "sys": "n5000-uk9.7.2.1.N1.1.bin",
        "status": "This is the log of last installation.\n
            Continuing with installation process, please wait.\n
            The login will be disabled until the installation is completed.\n
            Performing supervisor state verification. \n
            SUCCESS\n
            Supervisor non-disruptive upgrade successful.\n
            Install has been successful.\n",
    }
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


def already_set(current_boot_options, system_image_file, kickstart_image_file):
    return current_boot_options.get('sys') == system_image_file \
        and current_boot_options.get('kick') == kickstart_image_file

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
            system_image_file=dict(required=True),
            kickstart_image_file=dict(required=False),
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

    if device.device_type == PLATFORM_JUNOS:
        module.fail_json(msg='Install OS for Juniper not supported.')

    system_image_file = module.params['system_image_file']
    kickstart_image_file = module.params['kickstart_image_file']

    if kickstart_image_file == 'null':
        kickstart_image_file = None

    device.open()
    current_boot_options = device.get_boot_options()
    changed = False
    if not already_set(current_boot_options, system_image_file, kickstart_image_file):
        changed = True

    if not module.check_mode and changed == True:
        if device.device_type == 'nxos':
            timeout = 600
            device.set_timeout(timeout)
            try:
                start_time = time.time()
                device.set_boot_options(system_image_file, kickstart=kickstart_image_file)
            except:
                pass
            elapsed_time = time.time() - start_time

            device.set_timeout(30)
            try:
                install_state = device.get_boot_options()
            except:
                install_state = {}

            while elapsed_time < timeout and not install_state:
                try:
                    install_state = device.get_boot_options()
                except:
                    time.sleep(10)
                    elapsed_time += 10
        else:
            device.set_boot_options(system_image_file, kickstart=kickstart_image_file)
            install_state = device.get_boot_options()

        if not already_set(install_state, system_image_file, kickstart_image_file):
            module.fail_json(msg='Install not successful', install_state=install_state)
    else:
        install_state = current_boot_options

    device.close()
    module.exit_json(changed=changed, install_state=install_state)

from ansible.module_utils.basic import *
main()
