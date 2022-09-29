# Copyright 2022
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

from __future__ import absolute_import, division, print_function

__metaclass__ = type


CONNECTION_ARGUMENT_SPEC = dict(
    platform=dict(
        choices=[
            "arista_eos_eapi",
            "cisco_aireos_ssh",
            "cisco_asa_ssh",
            "cisco_ios_ssh",
            "cisco_nxos_nxapi",
            "f5_tmos_icontrol",
            "juniper_junos_netconf",
        ],
        required=False,
        type="str",
    ),
    host=dict(required=False, type="str"),
    port=dict(required=False, type="str"),
    username=dict(required=False, type="str"),
    password=dict(required=False, type="str", no_log=True),
    secret=dict(required=False, type="str", no_log=True),
    transport=dict(required=False, choices=["http", "https"], type="str"),
    ntc_host=dict(required=False, type="str"),
    ntc_conf_file=dict(required=False, type="str"),
)

MUTUALLY_EXCLUSIVE = [
    ["host", "ntc_host"],
    ["ntc_host", "secret"],
    ["ntc_host", "transport"],
    ["ntc_host", "port"],
    ["ntc_conf_file", "secret"],
    ["ntc_conf_file", "transport"],
    ["ntc_conf_file", "port"],
]

REQUIRED_ONE_OF = ["host", "ntc_host", "provider"]
