[![Build Status](https://travis-ci.org/networktocode/ntc-ansible.svg?branch=master)](https://travis-ci.org/networktocode/ntc-ansible)

# Ansible Modules for Network Automation
### *And even get structured data back from CLI devices!*

---
### Requirements
* netmiko
* TextFSM (https://code.google.com/p/textfsm/)
* terminal

---
### Modules

  * [ntc_show_command - gets config data from devices that don't have an api](#ntc_show_command)
  * [ntc_config_command - writes config data to devices that don't have an api](#ntc_config_command)

---

## ntc_show_command
Gets config data from devices that don't have an API

  * [Synopsis](#synopsis)
  * [``platform`` Naming Convention](#platform-naming-convention)
  * [Options](#options)
  * [Examples](#examples)

#### Synopsis
This module offers structured data for CLI enabled devices by using the TextFSM library for templating and netmiko for SSH connectivity.

#### ``platform`` Naming Convention
The ``platform`` parameter given to the modules should be of the form:``<netmiko_device_type>[-<hardware_type>]``.
In plain English, that means it should start with a supported ``netmiko`` device type, followed by an optional hyphen
and arbitrary hardware specific identifier.

Valid ``platform`` names:
```
cisco_ios-c3k
cisco_ios-c6k
cisco_ios
cisco_nxos
hp_comware
```

Invalid ``platform`` names:
```
cisco-ios-c3k
csco_ios
hp-comware_5900
```

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| username  |   no  |  | <ul></ul> |  Username used to login to the target device  |
| platform  |   yes  |  ssh  | <ul></ul> |  Platform FROM the index file  |
| template_dir  |   no  |  ntc_templates  | <ul></ul> |  path where TextFSM templates are stored. Default path is ntc with ntc in the same working dir as the playbook being run  |
| host  |   no  |  | <ul></ul> |  IP Address or hostname (resolvable by Ansible control host)  |
| connection  |   no  |  ssh  | <ul> <li>ssh</li>  <li>offline</li> </ul> |  connect to device using netmiko or read from offline file for testing  |
| command  |   yes  |  | <ul></ul> |  Command to execute on target device  |
| file  |   no  |  | <ul></ul> |  If using connection=offline, this is the file (with path) of a file that contains raw text output, i.e. 'show command' and then the contents of the file will be rendered with the the TextFSM template  |
| password  |   no  |  | <ul></ul> |  Password used to login to the target device  |
| index_file  |   no  |  index  | <ul></ul> |  name of index file.  file location must be relative to the template_dir  |
| port | no | 22 | <ul></ul> | specify an alternative ssh port |
| delay | no | 1 | <ul></ul> | wait for command output from a target device |

#### Examples

```

# get vlan data
- ntc_show_command:
    connection: ssh
    platform: cisco_nxos
    command: 'show vlan'
    host: {{ inventory_hostname }}
    username: {{ username }}
    password: {{ password }}

```

## ntc_config_command
Writes config data to devices that don't have an API

  * [Synopsis](#ntc_config_synopsis)
  * [Options](#ntc_config_options)
  * [Examples](#ntc_config_examples)

### ntc_config_synopsis
This module writes configuration data to non-API enabled devices, via CLI, using netmiko for SSH connectivity.

### ntc_config_options

| Parameter     | Required | Default | Choices | Comments                                                                                                                                           |
|---------------|----------|---------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| username      | no       |         |         | Username used to login to the target device                                                                                                        |
| password      | no       |         |         | Password used to login to the target device                                                                                                        |
| secret        | no       |         |         | Specify the administrative password to allow ntc_config_command to make changes. On cisco devices, this is the equivalent to the enable password.   |
| connection    | no       | ssh     | ssh     | Connect to device using netmiko                                                                                                                    |
| port          | no       | 22      |         | Specify the port for netmiko to SSH to. The default is 22.                                                                                         |
| platform      | yes      |         |         | Required by netmiko in order to use the proper connection module for the type of device. It follows the same naming scheme as the ntc_show_command |
| host          | yes      |         |         | IP Address or hostname (resolvable by Ansible control host)                                                                                        |
| commands      | no       |         |         | Commands should be in a list format. config t isn't needed, as netmiko will automatically enter config mode to execute commands                    |
| commands_file | no       |         |         | the commands_file option can be very useful if you generate commands based upon the results of a ntc_show_command play.                            |

### ntc_config_examples

Example using the commands option
```
# write vlan data
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
Example using the commands_file option
```
# write config from file
- ntc_config_command:
    connection: ssh
    platform: cisco_ios
    commands_file: "dynamically_created_config.txt"
    host: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secret: "{{ secret }}"
```
---


---
Created by Network to Code, LLC
For:
2015
