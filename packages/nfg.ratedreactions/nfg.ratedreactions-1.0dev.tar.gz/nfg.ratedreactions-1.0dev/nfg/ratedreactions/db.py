from zope.interface import implements
from zope.component import getUtility
from persistent import Persistent

from collective.lead import Database
from sqlalchemy.engine.url import URL
import sqlalchemy as sa

from nfg.ratedreactions.interfaces import IRatedReaction
from nfg.ratedreactions.interfaces import IDatabaseSettings

class RatedReaction(object):
    implements(IRatedReaction)
    
    contextid = author = rating = title = body = text = date = None

class RatedReactionDatabaseSettings(Persistent):
    implements(IDatabaseSettings)

    drivername='mysql'
    hostname='127.0.0.1' # break out of the chroot
    port=None
    username='test'
    password='test'
    database='test'

class RatedReactionDatabase(Database):
    """SQL mapper for rated reactions.

set up the test

    >>> from zope.component import provideUtility
    >>> provideUtility(RatedReactionDatabase(),name='nfg.ratedreactions')

get the database connector 

    >>> from zope.component import getUtility
    >>> from collective.lead.interfaces import IDatabase
    >>> db = getUtility(IDatabase, name='nfg.ratedreactions')

For MySQL use:
    CREATE TABLE `ratedreaction` (
            `id` int(11) NOT NULL auto_increment,
            `contextid` int(11) NOT NULL,
            `author` varchar(128) NOT NULL,
            `rating` int(11) NOT NULL,
            `title` varchar(128) NOT NULL,
            `body` text NOT NULL,
            `date` datetime default NULL,
            PRIMARY KEY  (`id`),
            KEY (`contextid`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8

    """

    @property
    def _url(self):
        settings = getUtility(IDatabaseSettings)
        return URL(
            drivername=settings.drivername,
            username=settings.username,
            password=settings.password,
            host=settings.hostname,
            port=settings.port,
            database=settings.database)

    def _setup_tables(self, metadata, tables):
        tables['ratedreaction'] = sa.Table("ratedreaction",
            metadata,
            sa.Column("id", sa.types.Integer, primary_key=True),
            sa.Column("contextid", sa.types.Integer),
            sa.Column("author", sa.types.String(128),),
            sa.Column("rating", sa.types.Integer),
            sa.Column("title", sa.types.String(128),),
            sa.Column("body", sa.types.Text),
            sa.Column("date", sa.types.DateTime),
            )

    def _setup_mappers(self, tables, mappers):
        mappers['ratedreaction'] = sa.orm.mapper(RatedReaction,
                                          tables['ratedreaction'])

