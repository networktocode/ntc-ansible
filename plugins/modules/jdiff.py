#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Network to Code (@networktocode) <info@networktocode.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible plugin definition for jdiff action plugin."""
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


DOCUMENTATION = """
---
module: jdiff
short_description: Ansible module for jdiff.
version_added: '1.1.0'
description:
    - Ansible module wrapper on jdiff python library.
requirements:
    - jdiff
author: Patryk Szulczewski (@pszulczewski)
options:
    check_type:
        description:
            - Check type supported by jdiff
        required: true
        type: str
    evaluate_args:
        description:
            - arguments for evaluate() method
        required: true
        type: dict
    jmespath:
        description:
            - JMESPath to extract specific values
        type: str
        default: "*"
    exclude:
        description:
            - list of keys to exclude
        type: list
        elements: str
"""

EXAMPLES = """
- name: "EXACT_MATCH - VALIDATE INTERFACE STATUS"
  jdiff:
    check_type: "exact_match"
    evaluate_args:
      reference_data: "{{ ref_data }}"
      value_to_compare: "{{ data_to_compare }}"
    exclude:
      - interfaceStatistics
  register: result
  vars:
    ref_data: |
      {
          "Ethernet1": {
              "status": "up",
              "interfaceStatistics": {
                  "inBitsRate": 3403.4362520883615,
                  "inPktsRate": 3.7424095978179257,
                  "outBitsRate": 16249.69114419833,
                  "updateInterval": 300,
                  "outPktsRate": 2.1111866059750692
              }
          }
      }
    data_to_compare: |
      {
          "Ethernet1": {
              "status": "down",
              "interfaceStatistics": {
                  "inBitsRate": 3413.4362520883615,
                  "inPktsRate": 3.7624095978179257,
                  "outBitsRate": 16259.69114419833,
                  "updateInterval": 300,
                  "outPktsRate": 2.1211866059750692
              }
          }
      }

- name: "TOLERANCE - VALIDATE PREFIXES ARE WITH 10% TOLERANCE"
  jdiff:
    check_type: "tolerance"
    evaluate_args:
      reference_data: "{{ ref_data }}"
      value_to_compare: "{{ data_to_compare }}"
      tolerance: 5
    jmespath: "*.*.ipv4.[accepted_prefixes]"
  register: result
  vars:
    ref_data: |
      {
          "10.1.0.0": {
              "address_family": {
                  "ipv4": {
                      "accepted_prefixes": 100,
                      "sent_prefixes": 1
                  }
              }
          }
      }
    data_to_compare: |
      {
          "10.1.0.0": {
              "address_family": {
                  "ipv4": {
                      "accepted_prefixes": 90,
                      "sent_prefixes": 0
                  }
              }
          }
      }

- name: "PARAMETER - VALIDATE PEER TYPE"
  jdiff:
    check_type: "parameter_match"
    evaluate_args:
      value_to_compare: "{{ data_to_compare }}"
      mode: match
      params:
        linkType: external
    jmespath: peers[*].[$ip$,linkType]
  register: result
  vars:
    data_to_compare: |
      {
          "peers": [
              {
                  "ip": "10.1.0.0",
                  "linkType": "external"
              },
              {
                  "ip": "10.2.0.0",
                  "linkType": "external"
              }
          ]
      }

- name: "REGEX - VALIDATE MAC FORMAT"
  jdiff:
    check_type: "regex"
    evaluate_args:
      value_to_compare: "{{ data_to_compare }}"
      regex: "^([0-9a-fA-F]{2}(:|-)){5}([0-9a-fA-F]{2})$"
      mode: match
    jmespath: interfaces.*.[$name$,burnedInAddress]
  register: result
  vars:
    data_to_compare: |
      {
          "interfaces": {
              "Management1": {
                  "burnedInAddress": "08:00:27:e6:b2:f8",
                  "name": "Management1"
              },
              "Management2": {
                  "burnedInAddress": "08-00-27-e6-b2-f9",
                  "name": "Management2"
              }
          }
      }

- name: "OPERATOR - VALIDATE RX LEVEL WITHIN RANGE"
  jdiff:
    check_type: "operator"
    evaluate_args:
      value_to_compare: "{{ data_to_compare }}"
      params:
        params:
          mode: in-range
          operator_data: [-8, -2]
    jmespath: ports[*].[$name$,RxPower]
  register: result
  vars:
    data_to_compare: |
      {
          "ports": [
              {
                  "name": "1/1",
                  "RxPower": -3.83,
                  "state": "Connected"
              },
              {
                  "name": "1/2",
                  "RxPower": -3.21,
                  "state": "Connected"
              }
          ]
      }
"""

RETURN = """
changed:
    description: Indicates if change was made - always False.
    returned: success
    type: bool
fail_details:
    description: output indicating where the check failed
    returned: success
    type: dict
success:
    description: Indicates if the check was successful.
    returned: success
    type: bool
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    """Module function."""
    argument_spec = dict(
        check_type=dict(type='str', required=True),
        evaluate_args=dict(type='dict', required=True),
        jmespath=dict(type='str', default='*'),
        exclude=dict(type='list', elements='str', default=[]),
    )

    AnsibleModule(
        argument_spec=argument_spec,
        required_together=[['check_type', 'evaluate_args']],
        supports_check_mode=True
    )


if __name__ == "__main__":  # pragma: no cover
    main()
