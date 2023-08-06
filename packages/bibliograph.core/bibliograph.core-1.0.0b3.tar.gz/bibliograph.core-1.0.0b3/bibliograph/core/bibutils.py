"""Functions to aid the calling of bibutils command line programs.

See <http://www.scripps.edu/~cdputnam/software/bibutils/>.
"""

__docformat__ = 'reStructuredText'
__author__  = 'Tom Gross <itconsense@gmail.com>'

# Standard library imports
import logging

# Local imports
from bibliograph.core.utils import bin_search


log = logging.getLogger('bibliograph.core')

commands = {'bib2xml':'bib2xml -un',
            'copac2xml':'copac2xml',
            'end2xml':'end2xml',
            'isi2xml':'isi2xml',
            'med2xml':'med2xml',
            'ris2xml':'ris2xml',
            'xml2bib':'xml2bib',
            'xml2end':'xml2end',
            'xml2ris':'xml2ris',
            'bib2bib':'bib2xml | xml2bib',
            'copac2bib':'copac2xml | xml2bib ',
            'end2bib':'end2xml -i utf8 | xml2bib -nl -nb -o utf8 ',
            'isi2bib':'isi2xml | xml2bib -nl -nb -o utf8 ',
            'med2bib':'med2xml | xml2bib -nl -nb -o utf8 ',
            'ris2bib':'ris2xml -i utf8 | xml2bib -nl -nb -o utf8',
            'bib2end':'bib2xml | xml2end -nb -o unicode',
            'bib2ris':'bib2xml | xml2ris -nb -o unicode',
            'copac2end':'copac2xml | xml2end ',
            'isi2end':'isi2xml | xml2end ',
            'med2end':'med2xml | xml2end ',
            'ris2end':'ris2xml | xml2end ',
            'end2ris':'end2xml | xml2ris ',
            'copac2ris':'copac2xml | xml2ris ',
            'isi2ris':'isi2xml | xml2ris ',
            'med2ris':'med2xml | xml2ris ',
            }

def _getKey(source_format, target_format):
    return '2'.join([source_format, target_format])


def _hasCommands(command):
    """ Check if a collection of piped commands is available

        >>> _hasCommands('python -o|python -wrt')
        True

        >>> _hasCommands(' something_strange -m | python')
        False

    """
    for cmd in command.split('|'):
        cmd = cmd.strip()
        if ' ' in cmd:
            cmd = cmd[:cmd.find(' ')]
        if bin_search(cmd, False) is False:
            log.warn('Command %s not found in search path!', cmd)
            return False
    return True

_marker = object()
def _getCommand(source_format, target_format, default=_marker):
    key = _getKey(source_format, target_format)
    command = commands.get(key, None)
    if command is None:
        raise ValueError, "No transformation from '%s' to '%s' found." \
              % (source_format, target_format)

    if not _hasCommands(command):
        if default is _marker:
            raise LookupError, "Command %s not found." % command
        else:
            return default
    return command
