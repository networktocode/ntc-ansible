
# Multi-vendor Ansible Collection for Network Automation

Multi-vendor collection of Ansible Modules to automate repeateable tasks and data gathering. As of release 1.0.0 this collection is used pyntc v1.0.0 for the backend logic.

## Modules

  * **ntc_show_command** - gets structured data from devices that don't have an API.  This module uses SSH to connect to devices but via the backend pyntc library.  Supports as many device types as netmiko supports.
  * **ntc_config_command** - sends commands to devices that don't have an API.  This module uses SSH to connect to devices but via the backend pyntc library.  Supports as many device types as netmiko supports.
  * **ntc_save_config** - saves the running config and optionally copies it to the Ansible control host for an offline backup.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_file_copy** - copies a file from the Ansible control host to a network device. Uses SSH for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_reboot** - reboots a network device. Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_rollback** - performs two major functions.  (1) Creates a checkpoint file or backup running config on box. (2) Rolls back to the previously created checkpoint/backup config.  Use case is to create the checkpoint/backup as the first task in a playbook and then rollback to it _if_ needed using block/rescue, i.e. try/except in Ansible. Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista.
  * **ntc_install_os** - installs a new operating system or just sets boot options.  Depends on platform.  Does not issue a "reload" command, but the device may perform an automatic reboot.  Common workflow is to use ntc_file_copy, ntc_install_os, and then ntc_reboot (if needed) for upgrades.  Uses SSH/netmiko for IOS, NX-API for Nexus, and eAPI for Arista. For Cisco stack switches pyntc leverages `install_mode` flag to install with the install command. This has an optional parameter of `install_mode` available on install_os.
  * **ntc_validate_schema** - Validate data against required schema using json schema.
  * **jdiff** - `jdiff` is a lightweight Python library allowing you to examine structured data. `jdiff` provides an interface to intelligently compare--via key presense/absense and value comparison--JSON data objects.

## Background

These modules have a long history of using multiple different python libraries, as of 1.0.0 release of pyntc, all functionality in these modules have been moved to pyntc for easier supportability.

As more functionality and enhancements are made to pyntc, those will map over into these modules to extend them.
