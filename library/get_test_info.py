#!/usr/bin/env python
#

DOCUMENTATION = '''
---

module: ansible_docstring
short_description: Create markdown file for a modules docs
description:
    - Offers ability to dynamically create local markdown files
      (web docs) to be used offline for custom modules without
      requiring use of 'make webdocs'.  Also works on Core modules.
    - Only a single dir is supported in this release (no recursive dirs)
author: Jason Edelman (@jedelman8)
requirements:
    - Ansible must be installed
    - Modules must have proper Ansible doc and example strings
    - 'modules' must be the variable name that is registered in the playbook
    - The Jinja template called ansible-docs.j2 is required
notes:
    - This module uses module_docs that that is part of the Ansible project
      to extract the required strings from Ansible modules
options:
    path:
        description:
            - absolute path to a directory where the Ansible module(s) are stored
        required: true
        default: null
        choices: []
        aliases: []
'''

EXAMPLES = '''
# FULL PLAYBOOK EXAMPLE
  - name: get docs and examples for modules
    ansible_docstring: path=/usr/share/ansible/files/
    register: modules

  - name: build web/markdown ansible docs
    template: src=templates/ansible-docs.j2 dest=web/ansiblefilesdoc.md
'''

from os import walk
from ansible.utils import module_docs


def main():

    module = AnsibleModule(
        argument_spec=dict(
            path=dict(default='tests'),
        ),
        supports_check_mode=False
    )

    path = module.params['path']

    if path[-1] != '/':
        path = path + '/'

    tests = []
    for (dirpath, dirnames, files) in walk(path):

        if dirpath:
            command = dirpath.split('/')[-1]
        if files and command:
            for each in files:
                if 'parsed' in each:                              # cisco_ios_show_ip_bgp_summary.parsed
                    filename = each.split('.parsed')[0]           # cisco_ios_show_ip_bgp_summary   |   cisco_ios-3k_show_vlan
                    platform = filename.split('_' + command)[0]   # cisco_ios  |  cisco_ios-3k
                    raw = filename + '.raw'
                    cmd = command.replace('_', ' ')
                    temp = dict(command=cmd, platform=platform,
                                rawfile=raw, parsedfile=each, path=dirpath)
                    tests.append(temp)

    module.exit_json(tests=tests)


from ansible.module_utils.basic import *
main()

# cisco_ios-3k_show_ip_bgp_summary.parsed