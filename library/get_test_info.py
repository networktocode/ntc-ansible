#!/usr/bin/env python
#

DOCUMENTATION = '''
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
'''

EXAMPLES = '''
- get_test_info:

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
