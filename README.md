
Docs currently being updated.

# Multi-vendor Ansible Modules for Network Automation

### Dependencies

To install the dependencies:

```
pip install ntc-ansible
```

There is a git sub-module now being used for the templates, so when you clone this repo for the templates and Ansible modules you should use the follow clone options:

Option 1:

```
git clone https://github.com/networktocode/ntc-ansible --recursive
```

Option 2:

```
git clone https://github.com/networktocode/ntc-ansible
git submodule update --init --recursive
```


### Modules

  * ntc_show_command - gets structured data from devices that don't have an API.  This module uses SSH to connect to devices.  Supports as many device types as netmiko supports.
  * ntc_config_command - sends commands to devices that don't have an API.  This module uses SSH to connect to devices.  Supports as many device types as netmiko supports.
  * ntc_save_config - saves the running config and optionally copies it to the Ansible control host for an offline backup.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * ntc_file_copy - copies a file from the Ansible control host to a network device. Uses SSH for IOS, NX-API for Nexus, and eAPI for Arista.
  * ntc_reboot - reboots a network device. Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * ntc_get_facts - gathers facts from a network device.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * ntc_rollback - performs two major functions.  (1) Creates a checkpoint file or backup running config on box. (2) Rolls back to the previously created checkpoint/backup config.  Use case is to create the checkpoint/backup as the first task in a playbook and then rollback to it _if_ needed using block/rescue, i.e. try/except in Ansible. Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * ntc_install_os - installs a new operating system or just sets boot options.  Depends on platform.  Does not issue a "reload" command, but the device may perform an automatic reboot.  Common workflow is to use ntc_file_copy, ntc_install_os, and then ntc_reboot (if needed) for upgrades.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.


### Documentation

Add link for docs.

### Examples

See [Examples](examples.md)
