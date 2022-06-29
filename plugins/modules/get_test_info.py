#!/usr/bin/python

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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---

module: get_test_info
short_description: Pull required info for tests templates automagically
description:
    - Offers ability to dynamically create a list of dictionaries
      with info required to test all templates.  This will loop through
      the tests dir and build each dictionary to have command, platform,
      rawfile, parsedfile, and path for each.
author: Jason Edelman (@jedelman8)
options:
    path:
        description:
            - location where tests are located
        required: true
        default: null
        choices: []
        aliases: []
"""

EXAMPLES = r"""
- get_test_info:

"""

from os import walk

from ansible.module_utils.basic import AnsibleModule


def main():
    """Main runner."""
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(default="tests"),
        ),
        supports_check_mode=False,
    )

    path = module.params["path"]

    if path[-1] != "/":
        path = path + "/"

    tests = []
    for (dirpath, _, files) in walk(path):

        if dirpath:
            command = dirpath.split("/")[-1]
        if files and command:
            for each in files:
                if "parsed" in each:  # cisco_ios_show_ip_bgp_summary.parsed
                    filename = each.split(".parsed")[0]  # cisco_ios_show_ip_bgp_summary   |   cisco_ios-3k_show_vlan
                    platform = filename.split("_" + command)[0]  # cisco_ios  |  cisco_ios-3k
                    raw = filename + ".raw"
                    cmd = command.replace("_", " ")
                    temp = dict(command=cmd, platform=platform, rawfile=raw, parsedfile=each, path=dirpath)
                    tests.append(temp)

    module.exit_json(tests=tests)


main()
