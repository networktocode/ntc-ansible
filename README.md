
# Multi-vendor Ansible Modules for Network Automation

You need to perform **two** steps to start using these modules.

1. Ensure this repository is in your Ansible module search path
2. Install Dependencies 


## Ensure Modules are you in your search path

First, understand what your search path is:

```
ntc@ntc:~/projects$ ansible --version
ansible 2.1.1.0
  config file = /etc/ansible/ansible.cfg
  configured module search path = ???
```

If you already have a search path configured, clone the repo (see options below) while you are in your search path.

If you have a "default" or No search path shown, open the config file that is shown in the output above, here that is `/etc/ansible/ansible.cfg`.  In that file, you'll see these first few lines:

```
[defaults]

# some basic default values...

inventory      = /etc/ansible/hosts
library        = /home/ntc/projects/
```

Add a path for `library` - this will become your search path.  Validate it with `ansible --version` after you make the change.

When you clone, do not forget to use `--recursive `!

**Option 1:**

```
git clone https://github.com/networktocode/ntc-ansible --recursive
```

**Option 2:**

```
git clone https://github.com/networktocode/ntc-ansible
cd ntc-ansible
git submodule update --init --recursive
```

Note: if you want to use **ntc_show_command** for parsing with ntc-templates, you navigate to that directory after the clone and run the setup.py file, e.g. `sudo python setup.py install`.


As a quick test and sanity use `ansible-doc` on one of the modules before trying to use them in a playbook.  For example, try this:

```
$ ansible-doc ntc_file_copy
```

If that works, Ansible can find the modules and you can proceed to installing the deps below.


## Install Dependencies

**Option 1:**

```
pip install ntc-ansible
```

**Option 2:**

_If you already cloned it above, you can just run the third statement below._

```
git clone https://github.com/networktocode/ntc-ansible
cd ntc-ansible
sudo python setup.py install
```


Additionally, you'll need `lxml` can install like this on Ubuntu:

```
sudo apt-get install zlib1g-dev libxml2-dev libxslt-dev python-dev
```

Every so often `terminal` is not installed and it may need to be installed manually:

```
pip install terminal
```


## Modules

  * **ntc_show_command** - gets structured data from devices that don't have an API.  This module uses SSH to connect to devices.  Supports as many device types as netmiko supports.
  * **ntc_config_command** - sends commands to devices that don't have an API.  This module uses SSH to connect to devices.  Supports as many device types as netmiko supports.
  * **ntc_save_config** - saves the running config and optionally copies it to the Ansible control host for an offline backup.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_file_copy** - copies a file from the Ansible control host to a network device. Uses SSH for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_reboot** - reboots a network device. Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_get_facts** - gathers facts from a network device.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_rollback** - performs two major functions.  (1) Creates a checkpoint file or backup running config on box. (2) Rolls back to the previously created checkpoint/backup config.  Use case is to create the checkpoint/backup as the first task in a playbook and then rollback to it _if_ needed using block/rescue, i.e. try/except in Ansible. Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_install_os** - installs a new operating system or just sets boot options.  Depends on platform.  Does not issue a "reload" command, but the device may perform an automatic reboot.  Common workflow is to use ntc_file_copy, ntc_install_os, and then ntc_reboot (if needed) for upgrades.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.

## Common Issues

### Ansible 2.10

In order to use this with Ansible 2.10 and greater, the `packaging` python library must be installed.

### Gather Facts

Starting in Ansible 2.1 there is a name space conflict when gathering facts. The below message will indicate the issues:

```
TASK [Gathering Facts] *************************************************************************
*Using module file /home/bdowling/src/ansible-modules/ntc-ansible/setup.cfg*
fatal: [rtr02]: FAILED! => {
    "failed": true, 
    "msg": "module (setup) is missing interpreter line"
}

msg: module (setup) is missing interpreter line

PLAY RECAP *************************************************************************************
rtr02              : ok=0    changed=0    unreachable=0    failed=1   
```

You can solve this by either changing the `gather_facts` to no, or removing the 3 `setup.XX` files.

Gather Facts Example: 
```
- hosts: test
  connection: local
  gather_facts: no
```

Remove Files Example:
```
rm ./setup.cfg
rm ./setup.py
rm ./ntc-templates/setup.py
```
See https://github.com/ansible/ansible/issues/20702 and https://github.com/ansible/ansible/pull/20717 for further details.

### This module requires TextFSM

Most often seen in virtual enviroments as per ansible's interpretation of which python binary you are using is not as expected. You can tell that you have reached this issue if you correctly have textfsm installed, but receive the following warning:

```
FAILED! => {"changed": false, "failed": true, "msg": "This module requires TextFSM"}
```
To fix this add the following to your inventory or similar to your `group_vars/all.yml`

```
[vars:all]
ansible_python_interpreter="/usr/bin/env python"
```
see https://github.com/ansible/ansible/issues/6345#issuecomment-181999529 for further details. 

## Examples

See [Examples](examples.md)

## Background

**ntc_show_command** and **ntc_config_command** were the first two modules written out of this group.  These two use netmiko for transport - this means if netmiko supports a given platform, these modules can be used.

All other modules support Nexus using pyntc, Arista using pyeapi, IOS using netmiko, and Juniper using PyEZ.

