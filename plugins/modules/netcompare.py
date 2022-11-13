#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Network to Code (@networktocode) <info@networktocode.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible plugin definition for jdiff action plugin."""
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


DOCUMENTATION = """
---
module: netcompare
short_description: Ansible module for netcompare.
version_added: '2.0.0'
description:
    - Ansible module for netcompare which is collections of predefined checks on various known data types.
requirements:
    - netcompare
author: Patryk Szulczewski (@pszulczewski)
options:
    collection_name:
        description:
            - Name of a check collection from netcompare
        required: true
        type: str
    check:
        description:
            - Name of a check in the collection
        required: true
        type: str
    evaluate_args:
        description:
            - arguments for evaluate() method in jdiff.CheckType
        required: true
        type: dict
"""

EXAMPLES = """
- name: "NETCOMPARE - VALIDATE INTERFACE STATUS"
  netcompare:
    collection_name: "sample"
    check: "check_interface_status"
    evaluate_args:
      reference_data: "{{ ref_data }}"
      value_to_compare: "{{ data_to_compare }}"
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

- name: "NETCOMPARE - CHECK ACCEPTED PREFIXES MATCH 10% DEFAULT TOLERANCE"
  netcompare:
    collection_name: "sample"
    check: "check_accepted_prefixes"
    evaluate_args:
      reference_data: "{{ ref_data }}"
      value_to_compare: "{{ data_to_compare }}"
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

- name: "NETCOMPARE - CHECK ACCEPTED PREFIXES MATCH 15% OWN TOLERANCE"
  netcompare:
    collection_name: "sample"
    check: "check_accepted_prefixes"
    evaluate_args:
      reference_data: "{{ ref_data }}"
      value_to_compare: "{{ data_to_compare }}"
      tolerance: 15  # overwrites default tolerance defined in yaml collection file
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

- name: "OPERATOR - VALIDATE RX LEVEL WITHIN RANGE (DEFAULT RANGE)"
  netcompare:
    collection_name: "sample"
    check: "check_optical_levels"
    evaluate_args:
      value_to_compare: "{{ data_to_compare }}"
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

- name: "OPERATOR - VALIDATE RX LEVEL WITHIN RANGE (OWN RANGE)"
  netcompare:
    collection_name: "sample"
    check: "check_optical_levels"
    evaluate_args:
      value_to_compare: "{{ data_to_compare }}"
      params:  # overwrites default params defined in yaml collection file
        params:
          mode: in-range
          operator_data: [-2, -1]
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
        collection_name=dict(type='str', required=True),
        check=dict(type='str', required=True),
        evaluate_args=dict(type='dict', required=True),
    )

    AnsibleModule(
        argument_spec=argument_spec,
        required_together=[['collection_name', 'check', 'evaluate_args']],
        supports_check_mode=True
    )


if __name__ == "__main__":  # pragma: no cover
    main()
