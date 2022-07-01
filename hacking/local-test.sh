#!/usr/bin/env bash

# Usage: ./hacking/local-test.sh

# Run build, which will remove previously installed versions
./hacking/build.sh

# Install new built version
ansible-galaxy collection install networktocode-netauto-*.tar.gz -p .

# You can now cd into the installed version and run tests
# (cd ansible_collections/networktocode/netauto/ && ansible-test units -v --python 3.8 && ansible-test sanity --requirements -v --python 3.8 --skip-test pep8 plugins/)
(cd ansible_collections/networktocode/netauto/ && ansible-test sanity --requirements -v --python 3.8 --skip-test pep8 plugins/ && ansible-test units -v --python 3.8)
rm -rf ansible_collections
