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
    - Validate schema with json schema.
author: "Ken Celenza (@itdependsnetworks)"
version_added: "2.6"
requirements:
    - jsonschema
options:
    schema:
        description:
            - A dictionary where each key is the name of the value to compare, and value is the schema in which to compare against.
        required: true
    data:
        description:
            - The data in which to verify, where each key is the name of the value to compare, generally hostvars[inventory_hostname].
        required: true
    scope:
        description:
            - The features in data which to use, which defines the scope of what keys to look for in schema and data.
        required: true
'''

EXAMPLES = '''
- name: 'VALIDATE THE SCHEMA'
  ntc_validate_schema:
    schema: '{{ my_schema }}'
    data: '{{ hostvars[inventory_hostname] }}'
    scope: '{{ scope }}'

- name: 'VALIDATE THE SCHEMA MANUAL'
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
      - name: "vlans"
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
        return False, "ValidationError: {0}".format(e.message)
    except SchemaError as e:
        return False, "SchemaError: {0}".format(e.message)
    except Exception as e:
        return False, "UnknownError: {0}".format(e.message)
    return True, ''


def main():
    argument_spec = dict(
        schema=dict(required=True, type="dict"),
        data=dict(required=True, type="dict"),
        scope=dict(required=True, type="list"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    if not HAS_LIB:
        module.fail_json(msg="jsonschema is required for this module.")

    schema = module.params["schema"]
    data = module.params["data"]
    scope = module.params["scope"]

    for item in scope:
        feature = item.get("name")
        required = item.get("required")
        if not feature:
            status = False
            msg = 'Malformed list item {0}, should be in format similar to ' \
                  '{1}'.format(item, '{"name": "feature", "required": True}')
        elif not schema.get(feature):
            status = False
            msg = "Schema was not defined for feature {0}. Schema key must match data key".format(feature)
        elif required and not data.get(feature):
            status = False
            msg = "Feature {0} required, but not found".format(feature)
        elif not data.get(feature):
            status = True
        else:
            status, msg = validate_schema(schema.get(feature), data.get(feature))

        if not status:
            resp = {
                "data": data.get(feature),
                "feature": feature,
                "message": msg,
            }

            module.fail_json(msg=resp)
    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
