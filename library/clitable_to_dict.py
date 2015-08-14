#!/usr/bin/env python

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


import clitable


def convert(cli_table):
    """Converts TextFSM cli_table object to list of dictionaries
    """

    # number of rows within the table excluding the headers
    object_rows = cli_table.size

    rows = []

    # build list of row objects - each row is list-like
    for each in range(0, object_rows):
        cli_table.row_index = each + 1
        rows.append(cli_table.row)

    objs = []
    for row in rows:
        temp = {}
        index = 0
        for each in row:
            temp[cli_table.header[index].lower()] = each
            index += 1
        objs.append(temp)

    return objs


if __name__ == "__main__":

    raw = open('cisco_show_vlan').read()

    cli_table = clitable.CliTable('index', '.')

    attrs = dict(Command='show vlan', vendor='cisco')

    cli_table.ParseCmd(raw, attrs)

    print convert(cli_table)
