#!/usr/bin/env python

#  Copyright 2018 Network to Code
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ntc_validate_schema
short_description: Validate schema with json schema
description:
  - Validate C(data) against required C(schema) using json schema.
author: "Ken Celenza (@itdependsnetworks)"
version_added: "2.6"
requirements:
  - jsonschema
options:
  data:
    description:
      - The data to validate against the C(schema).
      - Each key that requires validation must also be a key in the C(schema) dictionary.
    required: true
    type: dict
  schema:
    description:
      - The schema that the C(data) must adhere to.
      - Each key should have another dictionary as its value.
      - The dictionary defined for each schema requires a 'type' key defining the expected data type.
      - Valid data types are defined by jsonschema L($Find link for data types)
    required: true
    type: dict
  scope:
    description:
      - The features in C(data) which should be validated against the defined C(schema).
      - The "name" key should have a value that is a dictionary key in both C(data) and C(schema).
    required: true
    type: dict
'''

EXAMPLES = '''
- name: "VALIDATE THE SCHEMA"
  ntc_validate_schema:
    schema: "{{ my_schema }}"
    data: "{{ hostvars[inventory_hostname] }}"
    scope: "{{ scope }}"
- name: "VALIDATE THE SCHEMA EXPLICIT"
  ntc_validate_schema:
    schema:
      vlans:
        type: "array"
      hostname:
        type: "string"
    data:
      vlans:
        - 10
        - 20
      hostname: "nyc-rs01"
    scope:
      - name: "hostname"
        required: true
'''

RETURN = '''
# Default return values
'''

from ansible.module_utils.basic import AnsibleModule

try:
    from jsonschema import validate, ValidationError, SchemaError, FormatChecker
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def validate_schema(schema, data):
    try:
        validate(data, schema, format_checker=FormatChecker())
    except ValidationError as e:
        return (False, "ValidationError: {0}".format(e.message))
    except SchemaError as e:
        return (False, "SchemaError: {0}".format(e.message))
    except Exception as e:
        return (False, "UnknownError: {0}".format(e.message))
    return (True, '')

def main():
    argument_spec = dict(
        schema=dict(required=True, type='dict'),
        data=dict(required=True, type='dict'),
        scope=dict(required=True, type='list')
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    if not HAS_LIB:
        module.fail_json(msg='jsonschema is required for this module.')

    schema = module.params['schema']
    data = module.params['data']
    scope = module.params['scope']

    for item in scope:
        feature = item.get('name')
        required = item.get('required')
        if not feature:
            status, msg = (False, 'Malformed list item {}, should be in format similar to {"name": "feature", "required": True}'.format(item))
        elif not schema.get(feature):
            status, msg = (False, 'Schema was not defined for feature {}. Schema key must match data key'.format(feature))
        elif required and not data.get(feature):
            status, msg = (False, 'Feature {} required, but not found'.format(feature))
        elif not data.get(feature):
            status = True
        else:
            status, msg = validate_schema(schema.get(feature), data.get(feature))

        if not status:
            resp = {"data": data.get(feature),
                    "feature": feature,
                    "message": msg}

            module.fail_json(msg=resp)
    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
