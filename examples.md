
# EXAMPLES

This is the example that exists within the GitHub repo.  Single playbook with a single task that gets back VLAN data as JSON from CLI enabled devices.  Ironically, both of these devices support APIs too, but this is to prove out that it works!


### Inventory File
```
[cisco:vars]
username=cisco
password=!cisco123!

[hp_comware:vars]
username=hp
password=hp123

[cisco]
n9396-1

[hp_comware]
hp1
```

### hp_comware group vars file
```
---

vendor: hp_comware
device_type: hp_comware


vlan_command: "display vlan brief"
```


### cisco group vars file
```
---

vendor: cisco
device_type: cisco_nxos

vlan_command: "show vlan"
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
        vendor: "{{ vendor }}"
        device_type: "{{ device_type }}"
        command: "{{ vlan_command }}"
        host: "{{ inventory_hostname }}"
        username: "{{ username }}"
        password: "{{ password }}"
      register: vlans

    - debug: var=vlans
```





```
ansible-playbook site.yml -i hosts

PLAY [GET STRUCTURED DATA BACK FROM CLI DEVICES] ****************************** 

TASK: [GET VLANS IN REAL TIME] ************************************************ 
ok: [hp1]
ok: [n9396-1]

TASK: [debug var=vlans] ******************************************************* 
ok: [hp1] => {
    "var": {
        "vlans": {
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
                    "name": "VLAN",
                    "vlan_id": "10"
                },
                {
                    "name": "VLAN",
                    "vlan_id": "20"
                },
                {
                    "name": "VLAN",
                    "vlan_id": "30"
                },
                {
                    "name": "VLAN",
                    "vlan_id": "200"
                },
                {
                    "name": "VLAN",
                    "vlan_id": "500"
                }
            ]
        }
    }
}
ok: [n9396-1] => {
    "var": {
        "vlans": {
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
                    "name": "WEB",
                    "status": "active",
                    "vlan_id": "10"
                },
                {
                    "name": "VLAN0020",
                    "status": "active",
                    "vlan_id": "20"
                },
                {
                    "name": "VLAN0030",
                    "status": "active",
                    "vlan_id": "30"
                },
                {
                    "name": "VLAN0040",
                    "status": "active",
                    "vlan_id": "40"
                },
                {
                    "name": "VLAN0050",
                    "status": "active",
                    "vlan_id": "50"
                }
            ]
        }
    }
}

PLAY RECAP ******************************************************************** 
hp1                        : ok=2    changed=0    unreachable=0    failed=0   
n9396-1                    : ok=2    changed=0    unreachable=0    failed=0   
```

