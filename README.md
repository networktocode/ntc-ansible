# Multi-Vendor Ansible Modules for Network Automation
### *And even get structured data back from CLI devices!*

---
### Requirements
* netmiko
* TestFSM
* terminal

---
### Modules

  * [ntc_show_command - gets config data from devices that don't have an api](#ntc_show_command)

---

## ntc_show_command
Gets config data from devices that don't have an API

  * Synopsis
  * Options
  * Examples

#### Synopsis
 This module offers structured data for CLI enabled devices by using the TextFSM library for templating and netmiko for SSH connectivity

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| username  |   yes  |  | <ul></ul> |  Username used to login to the target device  |
| vendor  |   yes  |  ssh  | <ul></ul> |  Vendor FROM the index file  |
| device_type  |   yes  |  ssh  | <ul></ul> |  netmiko device type  |
| template_dir  |   no  |  ntc  | <ul></ul> |  path where TextFSM templates are stored. Default path is ntc with ntc in the same working dir as the playbook being run  |
| host  |   yes  |  | <ul></ul> |  IP Address or hostname (resolvable by Ansible control host)  |
| connection  |   no  |  ssh  | <ul> <li>ssh</li>  <li>offline</li> </ul> |  connect to device using netmiko or read from offline file for testing  |
| command  |   no  |  | <ul></ul> |  Command to execute on target device  |
| file  |   no  |  | <ul></ul> |  If using connection=offline, this is the file (with path) of a file that contains raw text output, i.e. 'show command' and then the contents of the file will be rendered with the the TextFSM template  |
| password  |   yes  |  | <ul></ul> |  Password used to login to the target device  |
| index_file  |   no  |  index  | <ul></ul> |  name of index file.  file location must be relative to the template_dir  |


 
#### Examples

```

# get vlan data
- ntc_show_command:
    connection=ssh
    vendor=cisco
    device_type=cisco_nxos
    command='show vlan'
    host={{ inventory_hostname }}
    username={{ username }}
    password={{ password }}


```



---


---
Created by Network to Code, LLC
For:
2015
