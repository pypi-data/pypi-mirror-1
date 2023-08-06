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
#             session.flush()
#             session.commit()
        session.flush()
__all__ = ['htmlentitydecoder', 'pwd', 'iter_in_transaction']
