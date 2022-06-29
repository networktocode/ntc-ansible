"""Simple split filter."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleFilterError


def split_string(string, separator=" "):
    """Splites a string on a separator."""
    try:
        return string.split(separator)
    except Exception as err:
        raise AnsibleFilterError("split plugin error: %s, string=%s" % str(err), str(string))  # pylint: disable=W0707


class FilterModule(object):  # pylint: disable=useless-object-inheritance
    """A filter to split a string into a list."""

    def filters(self):
        """Ansible filter."""
        return {"split": split_string}
