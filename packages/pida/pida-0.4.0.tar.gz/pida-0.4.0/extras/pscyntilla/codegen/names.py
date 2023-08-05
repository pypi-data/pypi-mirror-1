__copyright__ = """"2006 by Tiago Cogumbreiro <cogumbreiro@users.sf.net>"""
__license__ = "LGPL <http://www.gnu.org/copyleft/lesser.txt>"

# Generates the constants module
import re

VAL_REGEX = re.compile('^val\s+(?P<name>\S+)\s*=\s*(?P<value>\S+)')

def _iterate_vals(fd):
    
    for line in fd:
        if line.strip().split() == ["cat", "Deprecated"]:
            break

        try:
            val = VAL_REGEX.match(line).groupdict()
            val['name'] = val['name'].upper()
            yield val['name'], val['value']

        except AttributeError:
            pass


def generate_constants(src_fd, dst_fd):
    # copyright for the constants module is almost useless but what the heck
    dst_fd.write('''__copyright__ = "2006 by Tiago Cogumbreiro <cogumbreiro@users.sf.net>"
__license__ = "LGPL <http://www.gnu.org/copyleft/lesser.txt>"
''')

    for key_val in _iterate_vals(src_fd):
        dst_fd.write("%s = %s\n" % key_val)

