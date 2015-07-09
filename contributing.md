# CONTRIBUTING

If you want to contribute you've got two options:

 1. You want to create a template for a command that does not yet have a template
 2. You want to update an already existing template to parse additional values

## File naming convention

All files submitted for a show command "X" of vendor "Y" should follow a strict naming convention:
```
base_filename + [_test_suffix] + extension
```

**base_filename:** `vendory_show_command_x`  
**Template extension:** `.template`  
**Raw test file extension:** `.raw`  
**Parsed test file extension:** `.parsed`  
**test_suffix:** `[1..]`

>Example: Cisco's `show vlan` command  
**template file:** cisco_show_vlan.template  
**raw test file:** cisco_show_vlan.raw  
**parsed test file:** cisco_show_vlan.parsed  

## Contributing a brand new temlpate

In order to contribute you need to do three things:

  1. Create a TextFSM template for a given show command and store it in [ntc_templates](ntc_templates/)
  2. Add that TextFSM template to the [index](ntc_templates/index).  **Device** needs to be included within the index as well.
  3. Create a test input file (containing the output of the show command) and its parsed equivalent. The former should have `.raw`
     extension, the latter should have `.parsed` extension and store these files in [tests/vendor](tests/vendor)

## Updating an existing template

In order to update an existing temlpate you need to do two things:

  1. Update the existing TextFSM template in [ntc_templates](ntc_templates/)
  2. Create a new set of test files (`.raw` and `.parsed`), append test suffix to the base filename and store them in [tests/vendor](tests/vendor)

## Template file testing

If you need to test template at any time use `test-template.yml` playbook and provide a template base filename.

Note: device support is needed in Netmiko prior to using here.

Documentation on TextFSM:  http://code.google.com/p/textfsm/wiki/TextFSMHowto

