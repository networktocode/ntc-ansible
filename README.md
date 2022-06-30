
# Multi-vendor Ansible Collection for Network Automation

Multi-vendor collection of Ansible Modules to automate repeateable tasks and data gathering.

## Modules

  * **ntc_show_command** - gets structured data from devices that don't have an API.  This module uses SSH to connect to devices.  Supports as many device types as netmiko supports.
  * **ntc_config_command** - sends commands to devices that don't have an API.  This module uses SSH to connect to devices.  Supports as many device types as netmiko supports.
  * **ntc_save_config** - saves the running config and optionally copies it to the Ansible control host for an offline backup.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_file_copy** - copies a file from the Ansible control host to a network device. Uses SSH for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_reboot** - reboots a network device. Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_get_facts** - gathers facts from a network device.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_rollback** - performs two major functions.  (1) Creates a checkpoint file or backup running config on box. (2) Rolls back to the previously created checkpoint/backup config.  Use case is to create the checkpoint/backup as the first task in a playbook and then rollback to it _if_ needed using block/rescue, i.e. try/except in Ansible. Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_install_os** - installs a new operating system or just sets boot options.  Depends on platform.  Does not issue a "reload" command, but the device may perform an automatic reboot.  Common workflow is to use ntc_file_copy, ntc_install_os, and then ntc_reboot (if needed) for upgrades.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista. For Cisco stack switches pyntc leverages `install_mode` flag to install with the install command. This has an optional parameter of `install_mode` available on install_os (requires PyNTC > 0.16.0)

## Examples

See [Examples](./docs/examples/examples.md/examples.md)

## Background

**ntc_show_command** and **ntc_config_command** were the first two modules written out of this group.  These two use netmiko for transport - this means if netmiko supports a given platform, these modules can be used.

All other modules support Nexus using pyntc, Arista using pyeapi, IOS using netmiko, and Juniper using PyEZ.
