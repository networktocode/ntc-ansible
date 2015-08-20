# CONTRIBUTING

There are two ways to contribute:

 1. Create a new template.
 2. Update an existing template.

## Creating a new template

  1. Create a TextFSM template for a given show command and store it in [ntc_templates](ntc_templates/)
  2. Add that TextFSM template to the [index file](ntc_templates/index).
  3. Create a test input file (containing the raw output of the show command) and give it the extension `.raw`.
  4. Create a file containing the correct parsed results and give it the extentsion `.parsed`.
  5. Store both the `.raw` and `.parsed` files in [tests/*devicetype*](tests/)
  6. (Optional) If creating more than one test case, i.e. more than one `.raw` and `.parsed` files, repeat steps
  3-5 but add a *test_suffix_number* to the files as described in *File naming conventions* below.

## Updating an existing template

  1. Update the existing TextFSM template in [ntc_templates](ntc_templates/)
  2. Repeat steps 3-6 from *Creating a new template* above.

## File naming conventions

All files submitted for a show command should follow a strict naming convention:
```
base_filename + [_test_suffix_number] + extension
```

**base_filename:** `*devicetype*_*commandname*`  
**Template extension:** `.template`  
**Raw test file extension:** `.raw`  
**Parsed test file extension:** `.parsed`  
**test_suffix_number:** `[*<integer>*]`

>Example: Cisco's `show vlan` command  
**template file:** cisco_ios_show_vlan.template  
**raw test file:** cisco_ios_show_vlan.raw  
**parsed test file:** cisco_ios_show_vlan.parsed

**alternate raw test file:** cisco_ios_show_vlan_1.raw  
**alternate parsed test file:** cisco_ios_show_vlan_1.parsed  

## Template file testing

To test a template, run `test-template.yml` as a playbook follow the prompts.

Note: 

* device types follow netmiko's conventions.
* device support in netmiko is required.

Documentation on TextFSM:  http://code.google.com/p/textfsm/wiki/TextFSMHowto
