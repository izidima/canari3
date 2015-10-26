import os
import re
import string
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from urlparse import urlparse, urlunparse

from canari.utils.fs import pushd
from resource import global_config
from canari.mode import is_local_exec_mode
from utils.wordlist import wordlist

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2015, Canari Project'
__credits__ = []

__license__ = 'GPLv3'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'CanariConfigParser',
    'load_config',
    'NoOptionError',
    'NoSectionError'
]

SECTION_LOCAL = 'canari.local'

SECTION_REMOTE = 'canari.remote'

OPTION_LOCAL_CONFIGS = 'canari.local.configs'

OPTION_LOCAL_PATH = 'canari.local.path'

OPTION_REMOTE_PACKAGES = 'canari.remote.packages'


class CanariConfigParser(SafeConfigParser):

    @staticmethod
    def _interpolate_environment_variables(value):
        if isinstance(value, str):
            value = string.Template(value).safe_substitute(os.environ)
        return value

    def _interpolate(self, section, option, value, d):
        return SafeConfigParser._interpolate(self, section, option, self._interpolate_environment_variables(value), d)

    def __iadd__(self, other):
        self.add_section(other)
        return self

    def __isub__(self, other):
        self.remove_section(other)
        return self

    def _parse_value(self, value):
        if value.startswith('object://') and is_local_exec_mode():
            r = urlparse(value)
            try:
                v = r.path.lstrip('/')
                m = __import__(r.netloc, globals(), locals(), [v])
                value = m.__dict__[v]
            except ImportError:
                pass
        elif re.match(r'^\d+$', value):
            value = int(value)
        elif re.match(r'^\d+\.\d+$', value):
            value = float(value)
        elif re.search(r'\s*(?<=[^\\]),+\s*', value):
            l = re.split(r'\s*(?<=[^\\]),+\s*', value)
            value = []
            for v in l:
                value.append(self._parse_value(v))
        else:
            value = value.replace(r'\,', ',')
        return value

    def _render_value(self, value):
        if isinstance(value, str):
            value = value.replace(',', '\\,')
        elif isinstance(value, list):
            value = ','.join([self._render_value(v) for v in value])
        # elif callable(value):
        #     value = urlunparse(('python', value.__module__, value.__name__, '', '', ''))
        else:
            value = str(value)
        return value

    def _get_option_value(self, key, raise_on_empty_option=False):
        if not key and raise_on_empty_option:
            raise KeyError("Invalid key %r, must be in '<section>.<option>'" % key)
        if self.has_section(key):
            return key, ''
        return key.rsplit('.', 1) if '.' in key else (key, '')

    def __getitem__(self, key):
        section, option = self._get_option_value(key, True)
        value = self.get(section, option)
        value = self._parse_value(value)
        if option == 'wordlist':
            value = wordlist(value)
        return value

    def __setitem__(self, key, value):
        if value.strip().startswith('object://'):
            raise ValueError('Cannot set object option.')
        section, option = self._get_option_value(key, True)
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, self._render_value(value))

    def __delitem__(self, key):
        section, option = self._get_option_value(key)
        if option:
            self.remove_option(section, option)
        else:
            self.remove_section(section)

    def __contains__(self, key):
        section, option = self._get_option_value(key)
        if option:
            return self.has_option(section, option)
        return self.has_section(section)

    def update(self, other):
        if not isinstance(other, CanariConfigParser):
            raise ValueError('Expected a CanariConfigParser, got %r instead' % type(other).__name__)
        self._sections.update(other._sections)


def load_config(config_file=None, recursive_load=True):
    if not config_file:
        config_file = os.path.join(os.getcwd(), 'canari.conf')
        if not os.path.lexists(config_file):
            config_file = os.path.join(os.path.expanduser('~'), '.canari', 'canari.conf')

    with pushd(os.path.dirname(config_file)):
        config_parser = CanariConfigParser()
        config_parser.read([global_config, config_file])
        if recursive_load and OPTION_LOCAL_CONFIGS in config_parser:
            config_parser.read(config_parser[OPTION_LOCAL_CONFIGS])
        return config_parser
