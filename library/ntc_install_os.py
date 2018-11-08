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

# fmt: off
DOCUMENTATION = '''
---
module: ntc_install_os
short_description: Install an operating system by setting the boot options
                   like boot image and kickstart image.
description:
    - Set boot options like boot image and kickstart image.
    - Supported platforms include Cisco Nexus switches with NX-API,
      Cisco IOS switches or routers, Arista switches with eAPI.
notes:
    - Do not include full file paths, just the name
      of the file(s) stored on the top level flash directory.
    - You must know if your platform supports taking a kickstart image as a parameter.
      If supplied but not supported, errors may occur.
    - It may be useful to use this module in conjuction with ntc_file_copy and ntc_reboot.
    - With F5, volume parameter is required.
    - With NXOS devices, this module attempts to install the software immediately,
      wich may trigger a reboot.
    - With NXOS devices, install process may take up to 10 minutes,
      especially if the device reboots.
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
        choices: ["cisco_nxos_nxapi", "arista_eos_eapi", "cisco_ios_ssh",
                  "cisco_asa_ssh", "f5_tmos_icontrol"]
    system_image_file:
        description:
            - Name of the system (or combined) image file on flash.
        required: true
    kickstart_image_file:
        description:
            - Name of the kickstart image file on flash.
        required: false
        default: null
    volume:
        description:
            - Volume name - required argument for F5 platform.
        required: false
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
        choices: ["http", "https"]
    port:
        description:
            - TCP/UDP port to connect to target device.
            - If omitted standard port numbers will be used. 80 for HTTP; 443 for HTTPS; 22 for SSH.
        required: false
        default: null
    ntc_host:
        description:
            - The name of a host as specified in an NTC configuration file.
        required: false
        default: null
    ntc_conf_file:
        description:
            - The path to a local NTC configuration file.
            - If omitted, and ntc_host is specified, the system will look for a file given
              by the path in the environment variable PYNTC_CONF, and then in the users
              home directory for a file called .ntc.conf.
        required: false
        default: null
    reboot:
        description:
            - Determines whether or not the device should be rebooted to complete OS installation.
        required: false
        default: false
'''

EXAMPLES = '''
vars:
  ios_provider:
    host: "{{ inventory_hostname }}"
    username: "ntc-ansible"
    password: "ntc-ansible"
    platform: "cisco_ios_ssh"
    connection: ssh

- name: "INSTALL OS ON NEXUS 9K"
  ntc_install_os:
    ntc_host: n9k1
    system_image_file: n9000-dk9.6.1.2.I3.1.bin
    reboot: yes

- name: "INSTALL OS ON NEXUS 3K WITH KICKSTART"
  ntc_install_os:
    ntc_host: n3k1
    system_image_file: n3000-uk9.6.0.2.U6.5.bin
    kickstart_image_file: n3000-uk9-kickstart.6.0.2.U6.5.bin
    reboot: yes

- name: "CONFIGURE BOOT OPTIONS ON CISCO 2800"
  ntc_install_os:
    ntc_host: c2801
    system_image_file: c2800nm-adventerprisek9_ivs_li-mz.151-3.T4.bin

- name: "INSTALL OS ON CISCO 2800"
  ntc_install_os:
    provider: "{{ ios_provider }}"
    system_image_file: c2800nm-adventerprisek9_ivs_li-mz.151-3.T4.bin
    reboot: yes
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

import time  # noqa E402

from ansible.module_utils.basic import AnsibleModule, return_values  # noqa E402

try:
    from pyntc import ntc_device, ntc_device_by_name  # noqa E402
    HAS_PYNTC = True
except ImportError:
    HAS_PYNTC = False

try:
    # TODO: Ensure pyntc adds __version__
    from pyntc import __version__ as pyntc_version
    HAS_PYNTC_VERSION = True
except ImportError:
    HAS_PYNTC_VERSION = False
# fmt: on

PLATFORM_NXAPI = "cisco_nxos_nxapi"
PLATFORM_IOS = "cisco_ios_ssh"
PLATFORM_EAPI = "arista_eos_eapi"
PLATFORM_F5 = "f5_tmos_icontrol"
PLATFORM_ASA = "cisco_asa_ssh"


# TODO: Remove when deprecating older pyntc
def already_set(boot_options, system_image_file, kickstart_image_file, **kwargs):
    volume = kwargs.get("volume")
    device = kwargs.get("device")
    if device and volume:
        return device.image_installed(image_name=system_image_file, volume=volume)

    return (
        boot_options.get("sys") == system_image_file
        and boot_options.get("kick") == kickstart_image_file
    )


def main():
    module = AnsibleModule(
        argument_spec=dict(
            platform=dict(
                choices=[PLATFORM_NXAPI, PLATFORM_IOS, PLATFORM_EAPI, PLATFORM_F5, PLATFORM_ASA],
                required=False,
            ),
            host=dict(required=False),
            username=dict(required=False, type="str"),
            password=dict(required=False, type="str", no_log=True),
            secret=dict(required=False, no_log=True),
            transport=dict(required=False, choices=["http", "https"]),
            port=dict(required=False, type="int"),
            provider=dict(type="dict", required=False),
            ntc_host=dict(required=False),
            ntc_conf_file=dict(required=False),
            system_image_file=dict(required=True),
            kickstart_image_file=dict(required=False),
            volume=dict(required=False, type="str"),
            reboot=dict(required=False, type="bool", default=False),
        ),
        mutually_exclusive=[
            ["host", "ntc_host"],
            ["ntc_host", "secret"],
            ["ntc_host", "transport"],
            ["ntc_host", "port"],
            ["ntc_conf_file", "secret"],
            ["ntc_conf_file", "transport"],
            ["ntc_conf_file", "port"],
        ],
        required_one_of=[["host", "ntc_host", "provider"]],
        required_if=[["platform", PLATFORM_F5, ["volume"]]],
        supports_check_mode=True,
    )

    if not HAS_PYNTC:
        module.fail_json(msg="pyntc Python library not found.")
    # TODO: Change to fail_json when deprecating older pyntc
    if not HAS_PYNTC_VERSION:
        module.warn("Support for pyntc version < 0.0.9 is being deprecated; please upgrade pyntc")

    # TODO: Remove warning when deprecating reboot option on non-F5 devices
    module.warn("Support for installing the OS without rebooting may be deprecated in the future")

    provider = module.params["provider"] or {}

    no_log = ["password", "secret"]
    for param in no_log:
        if provider.get(param):
            module.no_log_values.update(return_values(provider[param]))

    # allow local params to override provider
    for param, pvalue in provider.items():
        # TODO: Figure out exactly the purpose of this and correct truthiness or noneness
        if module.params.get(param) != False:
            module.params[param] = module.params.get(param) or pvalue

    platform = module.params["platform"]
    host = module.params["host"]
    username = module.params["username"]
    password = module.params["password"]

    ntc_host = module.params["ntc_host"]
    ntc_conf_file = module.params["ntc_conf_file"]

    transport = module.params["transport"]
    port = module.params["port"]
    secret = module.params["secret"]
    reboot = module.params["reboot"]

    # TODO: Remove checks if we require reboot for non-F5 devices
    if platform == "cisco_nxos_nxapi" and not reboot:
        module.fail_json(msg="NXOS requires setting the \"reboot\" parameter to True")
    if platform != "cisco_nxos_nxapi" and reboot and not HAS_PYNTC_VERSION:
        module.fail_json(msg="Using the \"reboot\" parameter requires pyntc version > 0.0.8")

    argument_check = {
        "host": host,
        "username": username,
        "platform": platform,
        "password": password,
    }
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    if ntc_host is not None:
        device = ntc_device_by_name(ntc_host, ntc_conf_file)
    else:
        kwargs = {}
        if transport is not None:
            kwargs["transport"] = transport
        if port is not None:
            kwargs["port"] = port
        if secret is not None:
            kwargs["secret"] = secret

        device_type = platform
        device = ntc_device(device_type, host, username, password, **kwargs)

    system_image_file = module.params["system_image_file"]
    kickstart_image_file = module.params["kickstart_image_file"]
    volume = module.params["volume"]

    if kickstart_image_file == "null":
        kickstart_image_file = None

    device.open()
    pre_install_boot_options = device.get_boot_options()

    if not module.check_mode:
        # TODO: Remove conditional when deprecating older pyntc
        if HAS_PYNTC_VERSION:
            # TODO: Remove conditional if we require reboot for non-F5 devices
            if reboot or device.device_type == "f5_tmos_icontrol":
                # TODO: Ensure all devices support install_os method and return the same values and raise exceptions
                changed = device.install_os(system_image_file, kickstart=kickstart_image_file, volume=volume)
            else:
                # TODO: Remove support if we require reboot for non-F5 devices
                changed = device.set_boot_options(system_image_file, kickstart=kickstart_image_file)

            if reboot and device.device_type == "f5_tmos_icontrol" and \
                pre_install_boot_options["active_volume"] != volume:
                try:
                    changed = True
                    device.reboot(confirm=True, volume=volume)
                except RuntimeError:
                    module.fail_json(
                        msg="Attempted reboot but did not boot to desired volume",
                        original_volume=pre_install_boot_options["active_volume"],
                        expected_volume=volume,
                    )

            # TODO: Move validation to pyntc and raise exception there
            install_state = device.get_boot_options()
            if changed:
                if device.device_type != "f5_tmos_icontrol" and system_image_file != install_state["sys"]:
                    module.fail_json(
                        msg="Attempted upgrade but did not boot to desired image",
                        original_image=pre_install_boot_options["sys"],
                        current_image=install_state["sys"],
                    )

        # TODO: Remove contents of else when deprecating older pyntc
        else:
            changed = False
            install_state = pre_install_boot_options

            if not already_set(
                boot_options=pre_install_boot_options,
                system_image_file=system_image_file,
                kickstart_image_file=kickstart_image_file,
                volume=volume,
                device=device,
            ):
                changed = True

                if device.device_type == "nxos":
                    timeout = 600
                    device.set_timeout(timeout)
                    try:
                        start_time = time.time()
                        device.set_boot_options(
                            system_image_file,
                            kickstart=kickstart_image_file,
                        )
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
                    device.set_boot_options(
                        system_image_file,
                        kickstart=kickstart_image_file,
                        volume=volume,
                    )
                    install_state = device.get_boot_options()

                    if not already_set(
                        boot_options=pre_install_boot_options,
                        system_image_file=system_image_file,
                        kickstart_image_file=kickstart_image_file,
                        volume=volume,
                        device=device,
                    ):
                        module.fail_json(msg="Install not successful", install_state=install_state)

    else:
        if HAS_PYNTC_VERSION:
            # TODO: Ensure all devices support private method
            changed = device._image_booted(system_image_file, kickstart=kickstart_image_file, volume=volume)
        # TODO: Remove contents of else when deprecating older pyntc
        else:
            changed = already_set(
                boot_options=pre_install_boot_options,
                system_image_file=system_image_file,
                kickstart_image_file=kickstart_image_file,
                volume=volume,
                device=device,
            )

        install_state = pre_install_boot_options

    device.close()
    module.exit_json(changed=changed, install_state=install_state)


main()
