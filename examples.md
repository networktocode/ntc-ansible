
# EXAMPLES


### Inventory File
```
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
```
---

platform: hp_comware

vlan_command: display vlan brief
```


### cisco_nxos group vars file
```
---

platform: cisco_nxos

vlan_command: show vlan
```


### Playbook
```
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

```
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

```
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

```
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

```
- ntc_save_config:
    platform=cisco_ios_ssh
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

Does an equivalent of a `copy run filename.cfg`

```
- ntc_save_config:
    platform=cisco_ios_ssh
    remote_file=filename.cfg
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

Does an equivalent of a `copy run start` **AND** saves a local copy to the local Ansible control host.

```
- ntc_save_config:
    platform=cisco_ios_ssh
    local_file=backups/{{ inventory_hostname }}.cfg
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

# Filter Plugins

##### ntc_parse

Get structured data back using TextFSM along with `ios_command` and `ntc_parse` filter plugin within Ansible.
```
---

- name: "Testing ntc_parse filter plugin"
  hosts: switch
  connection: network_cli
  become: yes
  become_method: enable
  gather_facts: no
  vars:
    command: show ip interface

  tasks:
    - name: "Gather data via show ip interface command"
      ios_command:
        commands: "{{ command }}"
      register: interfaces

    - name: "Test NTC template filters"
      set_fact:
        interfaces_struct: "{{ interfaces.stdout.0 | ntc_parse(command, 'cisco_ios', '/home/ntc-templates/templates/') }}"

    - name: "Debug interfaces_struct"
      debug:
        var: interfaces_struct
```
Requirements:

This requires the filter_plugins to be set in ansible.cfg to the directory that ntc_parse filter lives in, ex. `/ntc-ansible/filter_plugins/`. This can be obtained by cloning this repository to a location on the Ansible host or installing ntc-ansible via Pip.

ntc_parse takes the following arguments:

`command` This is the command that was ran to collect the output to be parsed

`platform` This is modeled after the name of the template being used, ex. cisco_ios_show_version.template

`template_dir` By default, this will attempt to dynamically learn the location, but may be set manually as well

Structured data output:
```
TASK [Debug interfaces_struct] *******************************************************************************************************************
ok: [switch] => {
    "interfaces_struct": [
        {
          "inbound_acl": "",
          "interface": "Vlan1",
          "ip_address": "192.168.1.1",
          "ip_helper": [
              "192.168.255.3"
            ],
          "link_status": "down",
          "mask": "26",
          "mtu": "",
          "outgoing_acl": "",
          "protocol_status": "down"
        }
    ]
}
```

For more details on all of the modules, please be sure to check out the [Docs](http://docs.networktocode.com)

