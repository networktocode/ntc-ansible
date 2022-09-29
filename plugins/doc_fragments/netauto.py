# -*- coding: utf-8 -*-

#  Copyright 2022 Network to Code
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

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    """Documentation fragment for netauto modules."""

    DOCUMENTATION = r"""
options:
    platform:
        description:
          - Switch platform based on Pyntc library.
        required: false
        default: null
        choices: [
            "arista_eos_eapi",
            "cisco_aireos_ssh",
            "cisco_asa_ssh",
            "cisco_ios_ssh",
            "cisco_nxos_nxapi",
            "f5_tmos_icontrol",
            "juniper_junos_netconf",
        ]
        type: str
    host:
        description:
          - Hostame or IP address of switch.
        required: false
        default: null
        type: str
    username:
        description:
          - Username used to login to the target device.
        required: false
        default: null
        type: str
    password:
        description:
          - Password used to login to the target device.
        required: false
        default: null
        type: str
    provider:
        description:
          - Dictionary which acts as a collection of arguments used to define the characteristics
            of how to connect to the device.
            Note - host, username, password and platform must be defined in either provider
            or local param.
            Note - local param takes precedence, e.g. hostname is preferred to provider['host'].
        required: false
        type: dict
        suboptions:
            platform:
                description:
                - Switch platform based on Pyntc library.
                required: false
                default: null
                choices: [
                    "arista_eos_eapi",
                    "cisco_aireos_ssh",
                    "cisco_asa_ssh",
                    "cisco_ios_ssh",
                    "cisco_nxos_nxapi",
                    "f5_tmos_icontrol",
                    "juniper_junos_netconf",
                ]
                type: str
            host:
                description:
                - Hostame or IP address of switch.
                required: false
                default: null
                type: str
            username:
                description:
                - Username used to login to the target device.
                required: false
                default: null
                type: str
            password:
                description:
                - Password used to login to the target device.
                required: false
                default: null
                type: str
            secret:
                description:
                    - Enable secret for devices connecting over SSH.
                required: false
                default: null
                type: str
            transport:
                description:
                    - Transport protocol for API-based devices.
                required: false
                default: null
                choices: [http, https]
                type: str
            port:
                description:
                - TCP/UDP port to connect to target device. If omitted standard port numbers will be used.
                    80 for HTTP; 443 for HTTPS; 22 for SSH.
                required: false
                default: null
                type: str
            ntc_host:
                description:
                - The name of a host as specified in an NTC configuration file.
                required: false
                default: null
                type: str
            ntc_conf_file:
                description:
                - The path to a local NTC configuration file. If omitted, and ntc_host is specified,
                    the system will look for a file given by the path in the environment variable PYNTC_CONF,
                    and then in the users home directory for a file called .ntc.conf.
                required: false
                default: null
                type: str
    secret:
        description:
            - Enable secret for devices connecting over SSH.
        required: false
        default: null
        type: str
    transport:
        description:
            - Transport protocol for API-based devices.
        required: false
        default: null
        choices: [http, https]
        type: str
    port:
        description:
          - TCP/UDP port to connect to target device. If omitted standard port numbers will be used.
            80 for HTTP; 443 for HTTPS; 22 for SSH.
        required: false
        default: null
        type: str
    ntc_host:
        description:
          - The name of a host as specified in an NTC configuration file.
        required: false
        default: null
        type: str
    ntc_conf_file:
        description:
          - The path to a local NTC configuration file. If omitted, and ntc_host is specified,
            the system will look for a file given by the path in the environment variable PYNTC_CONF,
            and then in the users home directory for a file called .ntc.conf.
        required: false
        default: null
        type: str
    """

    COMMAND_OPTION = r"""
options:
  commands:
      description:
          - Command to execute on target device
      required: false
      default: null
      type: list
  commands_file:
      description:
          - Command to execute on target device
      required: false
      type: str
    """
