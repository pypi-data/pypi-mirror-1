# Copyright 2009, Red Hat, Inc
# Copyright 2009, Yaakov Nemoy
#
# This software may be freely redistributed under the terms of the GNU
# general public license, version 2 or higher.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from __future__ import with_statement

import re
import configobj

from contextlib import contextmanager
from htmlentitydefs import name2codepoint
from os import chdir, getcwd


def htmlentitydecoder(s):
    # first we scrub all named entities into normalacy.
    s1 = re.sub('&(%s);' % '|'.join(name2codepoint),
	lambda m: unichr(name2codepoint[m.group(1)]), s)
    #then we scrub the ones that are numeric instead
    return re.sub('&#(\d*?);', lambda m: unichr(int(m.group(1))), s1)

@contextmanager
def pwd(dir):
    old_dir = getcwd()
    chdir(dir)
    yield
    chdir(old_dir)

def iter_in_transaction(session, iter):
    with session.begin(subtransactions=True):
        for item in iter:
            yield item
        session.flush()

def iter_each_transaction(session, iter):
    for item in iter:
        with session.begin(subtransactions=True):
            yield item
        session.flush()


def last(l):
    return l[-1]


class OptionManager(object):
    def __init__(self, files, primary_file=None, hardcoded_defaults=dict()):
        primary_file = primary_file if primary_file else \
            (last(files) if files else None)

        files = (configobj.ConfigObj(f) for f in files)
        opts = reduce(configobj.ConfigObj.update, files)
        if hardcoded_defaults:
            cfg = hardcoded_defaults.update(opts)
        self.opts = configobj.ConfigObj(cfg)
        self.set_primary_file(primary_file)

        #TODO: update to a proper property once ymn upgrades to Fedora 11
        def set_primary_file(self, filename):
            self.opts.filename = filename
            self.primary_file = filename

        def get_primary_file(self):
            return primary_file

        def write(self):
            if self.primary_file:
                self.opts.write()

        def update(other):
            self.opts.update(other)


class LayeredOptionManager(object):
    def __init__(self, layers, primary_layer=None, hardcoded_defaults=dict()):
        self.layers = dict()
        self.primary_layer = primary_layer
        for layer, files in layers:
            if not type(files) is list:
                files = [files]
            self.layers[layer] = OptionManager(files)
        self.layers['hardcoded_defaults'] = hardcoded_defaults
        self.layers['runtime'] = dict()

    def update(self, other):
        self.layers['runtime'].update(other)

    def write_runtime_to_primary(self):
        self.primary.update(self.runtime)
        self.layers['runtime'] = dict()
        self.primary.write()

    @property
    def runtime(self):
        return self.layers['runtime']

    @property
    def primary(self):
        return self.layers[self.primary_layer]

    @property
    def hardcoded_defaults(self):
        return self.layers['hardcoded_defaults']

    def write(self):
        for layer in self.layers.values():
            layer.write()

__all__ = ['htmlentitydecoder', 'pwd', 'iter_in_transaction',
           'OptionManager', 'LayeredOptionManager']
