
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
    platform=cisco_ios
    command='show vlan'
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}

```

##### ntc_config_command

Send commands list.

```
- ntc_config_command:
    connection: ssh
    platform: cisco_ios
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
    platform: cisco_ios
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
    platform=cisco_ios
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

Does an equivalent of a `copy run filename.cfg`

```
- ntc_save_config:
    platform=cisco_ios
    remote_file=filename.cfg
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

Does an equivalent of a `copy run start` **AND** saves a local copy to the local Ansible control host.

```
- ntc_save_config:
    platform=cisco_ios
    local_file=backups/{{ inventory_hostname }}.cfg
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}
```

For more details on all of the modules, please be sure to check out the [Docs](http://docs.networktocode.com)

