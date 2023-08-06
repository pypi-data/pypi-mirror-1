# Copyright 2009, Red Hat, Inc
# Copyright 2009, Yaakov Nemoy
#
# This software may be freely redistributed under the terms of the GNU
# general public license, version 2 or higher.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from configobj import ConfigObj

from migrate.versioning.shell import main

import ekg.util
import ekg.model
import ekg.migration

from ekg.grapher import write_graph_page
from ekg.model import get_engine

UPDATE_ALL = True
CACHE_DIR = '.'

commands = list()

def command(f):
    global commands
    commands.append(f)
    return f


@command
def generate_tables():
    config = ConfigObj('settings.ini')
    db = config['dburi']
    engine = get_engine(db)
    ekg.model.metadata.create_all(engine)


@command
def scan():
    config = ConfigObj('settings.ini')
    global CACHE_DIR
    global UPDATE_ALL
    CACHE_DIR = config['cache_dir']
    UPDATE_ALL = config['update_all']
    ekg.model.UPDATE_ALL = UPDATE_ALL
    ekg.model.CACHE_DIR = CACHE_DIR
    for list, source \
            in ekg.util.iter_in_transaction(session, config['lists'].items()):
        StreamClass = stream_classes[source]
        stream = StreamClass.create_or_update(name=list)
    session.flush()
    session.commit()


@command
def graph():
    write_graph_page('001')


@command
def migrate():
    pth = ekg.migration.__path__[0]
    config = ConfigObj('settings.ini')
    db = config['dburi']
    main(url=db, repository=pth)


@command
def create_db():
    pth = ekg.migration.__path__[0]
    config = ConfigObj('settings.ini')
    db = config['dburi']
    engine = get_engine(db)
    con = engine.connect()
    con.close()
    main(['version_control'], url=db, repository=pth)


@command
def upgrade():
    pth = ekg.migration.__path__[0]
    config = ConfigObj('settings.ini')
    db = config['dburi']
    main(['upgrade'], url=db, repository=pth)


@command
def setup():
    create_db()
    upgrade()


__all__ = ['generate_tables', 'scan', 'graph', 'migrate', 'upgrade', 'setup', 'create_db']
