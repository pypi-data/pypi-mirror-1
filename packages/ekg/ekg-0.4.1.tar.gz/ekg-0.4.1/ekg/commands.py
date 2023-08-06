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
from ekg.core import Core

defaults = ConfigObj(unrepr=True)
defaults['update_all'] = True
defaults['cache_dir']  = '.'

commands = list()

def command(f):
    global commands
    commands.append(f)
    return f


@command
def generate_tables():
    config = ConfigObj('settings.ini', unrepr=True)
    core = Core(config)
    engine = core.engine
    ekg.model.metadata.create_all(engine)


@command
def scan():
    config = ConfigObj('settings.ini', unrepr=True)
    core = Core(config)
    session = core.session()
    for list, source \
            in ekg.util.iter_each_transaction(session, config['lists'].items()):
        StreamClass = ekg.model.stream_classes[source]
        stream = StreamClass.create_or_update(core, name=list)
#         session.flush()
#         session.commit()


@command
def graph():
    write_graph_page('001')


@command
def migrate():
    pth = ekg.migration.__path__[0]
    config = ConfigObj('settings.ini', unrepr=True)
    db = config['dburi']
    main(url=db, repository=pth)


@command
def create_db():
    pth = ekg.migration.__path__[0]
    config = ConfigObj('settings.ini', unrepr=True)
    db = config['dburi']

    # this creates the db in sqlite and ensures its accessible in other DBs
    core = Core(config)
    engine = core.engine
    con = engine.connect()
    con.close()

    main(['version_control'], url=db, repository=pth)


@command
def upgrade():
    pth = ekg.migration.__path__[0]
    config = ConfigObj('settings.ini', unrepr=True)
    db = config['dburi']
    main(['upgrade'], url=db, repository=pth)


@command
def setup():
    create_db()
    upgrade()


__all__ = ['generate_tables', 'scan', 'graph', 'migrate', 'upgrade', 'setup', 'create_db']
