#!/usr/bin/python

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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "community"}

DOCUMENTATION = r"""
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
      - Each key that requires validation mush also be the value for the "name" key in one of the
        C(scope) dictionaries.
      - A good strategy would be to use hostvars[inventory_hostname] to get all vars for the host
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
      - The "required" key is used to validate whether the C(data) must be present.
    required: true
    type: list
"""

EXAMPLES = r"""
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
      - name: "vlans"
"""

RETURN = r"""
# Default return values
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from jsonschema import FormatChecker, SchemaError, validate, ValidationError

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def validate_schema(schema, data):
    """Validate schema is correct."""
    try:
        validate(data, schema, format_checker=FormatChecker())
    except ValidationError as err:
        return False, "ValidationError: {0}".format(err.message)
    except SchemaError as err:
        return False, "SchemaError: {0}".format(err.message)
    except Exception as err:  # pylint: disable=broad-except
        return False, "UnknownError: {0}".format(err)
    return True, ""


def main():
    """Main execution."""
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
        # Make sure scope had a "name" key
        try:
            feature = item["name"]
        except KeyError:
            module.fail_json(
                msg="Malformed list item {0}, "  # noqa  # pylint: disable=missing-format-argument-key
                'should be in format similar to {"name": "feature", "required": True}'.format(item)
            )
        required = item.get("required")
        entry_data = data.get(feature)

        # Provide schema validation against data when data is present
        if entry_data is not None:
            entry_schema = schema.get(feature)
            # Validate the data against the schema when data is propely defined
            if entry_schema is not None:
                status, msg = validate_schema(entry_schema, entry_data)
            # Provide module.fail_json data when there is no schema defined for current required feature
            else:
                status = False
                msg = "Schema was not defined for feature {0}. Schema key must match data key".format(feature)
        # Provide module.fail_json data when there is no data defined for current required feature
        elif required:
            status = False
            msg = "Feature {0} required, but not found".format(feature)
        # Default to proper validation when scope is not required and data was not defined
        else:
            status = True

        # Fail the module when it did not pass validation or data/schema data was invalid
        if not status:
            resp = {
                "data": entry_data,
                "schema": entry_schema,
                "feature": feature,
                "msg": msg,
            }
            module.fail_json(**resp)

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
