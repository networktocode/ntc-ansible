#!/usr/bin/python

# Copyright 2015 Michael Kashin  <mmkashin@gmail.com>
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
module: compare_dict
short_description: verify that ntc template test case passes
description:
    - This module verifies that the result received from TextFSM
      for a particular template matches the expected output from
      a test scenario. It does so by comparing two lists of
      dictionaries going through elements of one and checking if
      the element 'is in' the second list.
author: Michael Kashin
requirements:
    - none
options:
    result:
        description:
            - a list of dictionaries received from ntc_show_command module
        required: true
        default: null
        choices: []
        aliases: []
    sample:
        description:
            - a parsed sample from a test scenario
        required: true
        default: null
        choices: []
        aliases: []

"""
EXAMPLES = r"""

# verify that parsed result is the same as expected
- compare_dict:
    result: "{{ item.item.response }}"
    sample: "{{ item.ansible_facts.parsed_sample }}"

"""

from ansible.module_utils.basic import AnsibleModule


def compare(list_one, list_two):
    """Compare two lists."""
    msg = ""
    for el in list_one:
        if el not in list_two:
            msg = str(el) + " is not found in sample input"
            return 1, msg
    return 0, msg


def main():
    """Main execution."""
    module = AnsibleModule(
        argument_spec=dict(
            result=dict(required=True),
            sample=dict(required=True),
        ),
        supports_check_mode=False,
    )

    result_dict = module.params["result"]
    sample_dict = module.params["sample"]

    rc, msg = compare(result_dict, sample_dict)

    if rc != 0:
        module.fail_json(msg=msg)
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()
