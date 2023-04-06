#!/usr/bin/env bash

# Usage: ./hacking/build.sh

# galaxy.yml build_ignore is not implemented in Ansible 2.9, so we have to delete files we don't want

# Remove previous test installs
rm -rf ~/.ansible/collections/ansible_collections/networktocode

# Remove old built versions
rm networktocode-netauto-1.0.0.tar.gz

# Remove test output
# rm -r tests/output
# rm -r .pytest_cache

ansible-galaxy collection build --force --verbose .
