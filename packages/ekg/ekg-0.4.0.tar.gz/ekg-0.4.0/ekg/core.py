# Copyright 2009, Red Hat, Inc
# Copyright 2009, Yaakov Nemoy
#
# This software may be freely redistributed under the terms of the GNU
# general public license, version 2 or higher.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys

import urlparse as up
import urlgrabber as ug

from urlgrabber.grabber import URLGrabber
from urlgrabber.progress import TextMultiFileMeter
from sqlalchemy.orm import sessionmaker, scoped_session, relation
from sqlalchemy import create_engine


class Core(object):
    def __init__(self, opts):
        self.opts = opts
        self.db = opts['dburi']
        self.engine = create_engine(self.db)
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=self.engine)
        self.progress_meter = TextMultiFileMeter(fo=sys.stdout)
        self.progress_meter.start()

    def new_grabber(self, **opts):
        ug_opts = dict(self.opts['urlgrabber'])
        ug_opts.update(opts)
        ug_opts['progress_obj'] = self.progress_meter.newMeter()
        return URLGrabber(**ug_opts)

    def create_or_update(self, cls, **remote):
        return cls.create_or_update(self, **remote)


