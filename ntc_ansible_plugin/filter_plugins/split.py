from ansible import errors
import re

def split_string(string, separator=' '):
    try:
        return string.split(separator)
    except Exception as e:
        raise errors.AnsibleFilterError('split plugin error: %s, string=%s' % str(e),str(string) )


class FilterModule(object):
    ''' A filter to split a string into a list. '''
    def filters(self):
        return {
            'split' : split_string
        }
