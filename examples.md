
# EXAMPLES


### Inventory File
```yaml
[cisco_nxos:vars]
username=cisco
password=cisco123

[hp_comware:vars]
username=hp
password=hp123

[cisco_nxos]
n9k1

[hp_comware]
hp1
```

### hp_comware group vars file
```yaml
---

platform: hp_comware

vlan_command: display vlan brief
```


### cisco_nxos group vars file
```yaml
---

platform: cisco_nxos

vlan_command: show vlan
```


### Playbook
```yaml
---

- name: GET STRUCTURED DATA BACK FROM CLI DEVICES
  hosts: all
  connection: local
  gather_facts: False

  tasks:

    - name: GET VLANS IN REAL TIME
      ntc_show_command:
        connection: ssh
        platform: "{{ platform }}"
        command: "{{ vlan_command }}"
        template_dir: "/home/ntc/ntc-templates/template" # Specifies where to search templates
        host: "{{ inventory_hostname }}"
        username: "{{ username }}"
        password: "{{ password }}"
      register: result

    - debug: var=result
```

```yaml
ansible-playbook site.yml -i hosts

PLAY [GET STRUCTURED DATA BACK FROM CLI DEVICES] ******************************

TASK: [GET VLANS IN REAL TIME] ************************************************
ok: [hp1]
ok: [n9k1]

TASK: [debug var=result] ******************************************************
ok: [hp1] => {
    "var": {
        "result": {
            "changed": false,
            "invocation": {
                "module_args": "",
                "module_name": "ntc_show_command"
            },
            "response": [
                {
                    "name": "VLAN",
                    "vlan_id": "1"
                },
                {
                    "name": "VLAN20",
                    "vlan_id": "20"
                }
            ]
        }
    }
}
ok: [n9k1] => {
    "var": {
        "result": {
            "changed": false,
            "invocation": {
                "module_args": "",
                "module_name": "ntc_show_command"
            },
            "response": [
                {
                    "name": "default",
                    "status": "active",
                    "vlan_id": "1"
                },
                {
                    "name": "VLAN0002",
                    "status": "active",
                    "vlan_id": "2"
                },
                {
                    "name": "VLAN0003",
                    "status": "active",
                    "vlan_id": "3"
                },
                {
                    "name": "VLAN0004",
                    "status": "active",
                    "vlan_id": "4"
                },
                {
                    "name": "VLAN0005",
                    "status": "active",
                    "vlan_id": "5"
                },
                {
                    "name": "VLAN0006",
                    "status": "active",
                    "vlan_id": "6"
                },
                {
                    "name": "VLAN0007",
                    "status": "active",
                    "vlan_id": "7"
                },
                {
                    "name": "VLAN0008",
                    "status": "active",
                    "vlan_id": "8"
                },
                {
                    "name": "VLAN0009",
                    "status": "active",
                    "vlan_id": "9"
                },
                {
                    "name": "test_segment",
                    "status": "active",
                    "vlan_id": "10"
                },
                {
                    "name": "VLAN0011",
                    "status": "active",
                    "vlan_id": "11"
                },
                {
                    "name": "VLAN0012",
                    "status": "active",
                    "vlan_id": "12"
                },
                {
                    "name": "VLAN0013",
                    "status": "active",
                    "vlan_id": "13"
                },
                {
                    "name": "VLAN0014",
                    "status": "active",
                    "vlan_id": "14"
                },
                {
                    "name": "VLAN0015",
                    "status": "active",
                    "vlan_id": "15"
                },
                {
                    "name": "VLAN0016",
                    "status": "active",
                    "vlan_id": "16"
                },
                {
                    "name": "VLAN0017",
                    "status": "active",
                    "vlan_id": "17"
                },
                {
                    "name": "VLAN0018",
                    "status": "active",
                    "vlan_id": "18"
                },
                {
                    "name": "VLAN0019",
                    "status": "active",
                    "vlan_id": "19"
                },
                {
                    "name": "peer_keepalive",
                    "status": "active",
                    "vlan_id": "20"
                },
                {
                    "name": "VLAN0022",
                    "status": "active",
                    "vlan_id": "22"
                },
                {
                    "name": "native",
                    "status": "active",
                    "vlan_id": "99"
                }
            ]
        }
    }
}

PLAY RECAP ********************************************************************
hp1                        : ok=2    changed=0    unreachable=0    failed=0
n9k1                       : ok=2    changed=0    unreachable=0    failed=0
```

# More Examples

##### ntc_show_command:

Get structured data (JSON) back using SSH to communicate to device.

```yaml
- ntc_show_command:
    connection=ssh
    platform=cisco_ios_ssh
    command='show vlan'
    template_dir: "/home/ntc/ntc-templates/template"
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}

```

##### ntc_config_command

Send commands list.

```yaml
- ntc_config_command:
    connection: ssh
    platform: cisco_ios_ssh
    commands:
      - vlan 10
      - name vlan_10
      - end
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"
```

Send commands from a file.

```yaml
- ntc_config_command:
    connection: ssh
    platform: cisco_ios_ssh
    commands_file: "dynamically_created_config.txt"
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"
```

##### ntc_file_copy

Copies file to remote device:

```yaml
- ntc_file_copy:
    local_file=images/ios.bin
    platform={{ platform }}
    username={{ un }}
    password={{ pwd }}
    host={{ inventory_hostname }}
```

##### ntc_save_config

Does an equivalent of a `copy run start`

```yaml
- ntc_save_config:
    platform=cisco_ios_ssh
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

Does an equivalent of a `copy run filename.cfg`

```yaml
- ntc_save_config:
    platform=cisco_ios_ssh
    remote_file=filename.cfg
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

Does an equivalent of a `copy run start` **AND** saves a local copy to the local Ansible control host.

```yaml
- ntc_save_config:
    platform=cisco_ios_ssh
    local_file=backups/{{ inventory_hostname }}.cfg
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

# Filter Plugins

##### ntc_parse

Get structured data back using TextFSM along with `*_command` and `ntc_parse` filter plugin within Ansible.
```yaml
---

- name: "TESTING NTC_PARSE FILTER PLUGIN"
  hosts: csr1000v 
  connection: network_cli
  gather_facts: no
  vars:
    ios_commands:
      - show ip interface
      - show lldp neighbors detail

  tasks:
    - name: "GATHER DATA VIA SHOW COMMANDS"
      ios_command:
        commands: "{{ ios_commands }}"
      register: command_output

    - name: "TEST NTC TEMPLATE FILTERS"
      set_fact:
        ip_interfaces: "{{ command_output.stdout.0 | ntc_parse(ios_commands[0], 'cisco_ios', '/home/ntc-templates/templates/') }}"
        lldp_neighbors: "{{ command_output.stdout.1 | ntc_parse(ios_commands[1], 'cisco_ios', '/home/ntc-templates/templates/') }}"

    - name: "DEBUG IP_INTERFACES"
      debug:
        var: ip_interfaces

    - name: "DEBUG LLDP_NEIGHBORS"
      debug:
        var: lldp_neighbors
```
Requirements:

This requires the filter_plugins to be set in ansible.cfg to the directory that ntc_parse filter lives in, ex. `/path/to/ntc-ansible/filter_plugins/`. This can be obtained by cloning this repository to a location on the Ansible host.

ntc_parse takes the following arguments:

`command` This is the command that was ran to collect the output to be parsed

`platform` This is modeled after the name of the template being used, ex. cisco_ios_show_version.template

`index` The index file is located within the `template_dir` and includes a list of available platform specific commands such as the example above. This can be modified to allow you to use custom templates that aren't in the upstream `ntc-templates` repo by simply adding them into the index file following the guidelines set within `ntc-templates`

`template_dir` By default, this will attempt to dynamically learn the location, and if this fails, it sets it to `ntc_templates/templates` or it can also be manually set as an argument passed into the filter.

Structured data output:
```yaml
TASK [DEBUG IP_INTERFACES] ******************************************************************************************************************************
ok: [csr1000v] => {
    "ip_interfaces": [
        {
            "inbound_acl": "",
            "intf": "GigabitEthernet1",
            "ip_helper": [],
            "ipaddr": [
                "172.16.1.232"
            ],
            "link_status": "up",
            "mask": [
                "24"
            ],
            "mtu": "1500",
            "outgoing_acl": "",
            "protocol_status": "up",
            "vrf": "Mgmt-intf"
        },
        {
            "inbound_acl": "",
            "intf": "GigabitEthernet2",
            "ip_helper": [],
            "ipaddr": [
                "10.0.0.17"
            ],
            "link_status": "up",
            "mask": [
                "30"
            ],
            "mtu": "1500",
            "outgoing_acl": "",
            "protocol_status": "up",
            "vrf": ""
        },
        {
            "inbound_acl": "",
            "intf": "GigabitEthernet3",
            "ip_helper": [],
            "ipaddr": [
                "10.0.0.13"
            ],
            "link_status": "up",
            "mask": [
                "30"
            ],
            "mtu": "1500",
            "outgoing_acl": "",
            "protocol_status": "up",
            "vrf": ""
        },
        {
            "inbound_acl": "",
            "intf": "Loopback0",
            "ip_helper": [],
            "ipaddr": [
                "192.168.0.4"
            ],
            "link_status": "up",
            "mask": [
                "32"
            ],
            "mtu": "1514",
            "outgoing_acl": "",
            "protocol_status": "up",
            "vrf": ""
        }
    ]
}

TASK [DEBUG LLDP_NEIGHBORS] *****************************************************************************************************************************
ok: [csr1000v] => {
    "lldp_neighbors": [
        {
            "capabilities": "B,R",
            "chassis_id": "fa16.3e99.72bd",
            "local_interface": "Gi2",
            "management_ip": "172.16.1.235",
            "neighbor": "nx-osv-1",
            "neighbor_interface": "to csr1000v-1",
            "neighbor_port_id": "Eth2/1",
            "system_description": "Cisco NX-OS(tm) titanium, Software (titanium-d1), Version 7.3(0)D1(1), RELEASE SOFTWARE Copyright (c) 2002-2013, 2015 by Cisco Systems, Inc. Compiled 1/11/2016 16:00:00",
            "vlan": ""
        },
        {
            "capabilities": "R",
            "chassis_id": "02dd.d868.a406",
            "local_interface": "Gi3",
            "management_ip": "10.0.0.14",
            "neighbor": "ios_xrv-1.virl.info",
            "neighbor_interface": "to csr1000v-1",
            "neighbor_port_id": "Gi0/0/0/0",
            "system_description": "Cisco IOS XR Software, Version 6.1.3[Default]",
            "vlan": ""
        },
        {
            "capabilities": "R",
            "chassis_id": "5e00.0002.0000",
            "local_interface": "Gi1",
            "management_ip": "172.16.1.234",
            "neighbor": "iosv-1.virl.info",
            "neighbor_interface": "OOB Management",
            "neighbor_port_id": "Gi0/0",
            "system_description": "Cisco IOS Software, IOSv Software (VIOS-ADVENTERPRISEK9-M), Version 15.6(3)M2, RELEASE SOFTWARE (fc2)",
            "vlan": ""
        }
    ]
}
```

For more details on all of the modules, please be sure to check out the [Docs](http://docs.networktocode.com)

