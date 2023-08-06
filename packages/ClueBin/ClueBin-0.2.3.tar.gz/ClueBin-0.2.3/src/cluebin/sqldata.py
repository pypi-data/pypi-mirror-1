import datetime
import sqlalchemy as sa
from sqlalchemy import orm
from cluebin import paste

metadata = sa.MetaData()
paste_table = sa.Table('pastes', metadata,
                       sa.Column('pasteid', sa.Integer, primary_key=True),
                       sa.Column('author_name', sa.Unicode(40)),
                       sa.Column('language', sa.Unicode(20)),
                       sa.Column('paste', sa.UnicodeText()),
                       sa.Column('date', sa.DateTime()))


class SqlPaste(paste.Paste):
    pass

orm.mapper(SqlPaste, paste_table)


class SqlPasteDataStore(paste.PasteDataStore):

    DEFAULT_ORDERING = [SqlPaste.date.desc(), SqlPaste.pasteid.desc()]

    def __init__(self, url, auto_create=False):
        super(SqlPasteDataStore, self).__init__()
        self.url = url
        if auto_create:
            self.setup_tables()

    @property
    def _engine(self):
        engine = getattr(self, '_cached_engine', None)
        if engine is not None:
            return engine
        engine = self._cached_engine = sa.create_engine(self.url)
        return engine

    @property
    def _session_factory(self):
        session_factory = getattr(self, '_cached_session_factory', None)
        if session_factory is None:
            session_factory = orm.sessionmaker(bind=self._engine,
                                               autoflush=True,
                                               transactional=True)
            self._cached_session_factory = session_factory
        return session_factory

    def _gen_session(self):
        return self._session_factory()

    def get_paste(self, pasteid):
        session = self._gen_session()
        return session.query(SqlPaste).filter(SqlPaste.pasteid==pasteid).one()

    def get_pastes(self):
        session = self._gen_session()
        res = session.query(SqlPaste)
        if self.DEFAULT_ORDERING:
            res = res.order_by(self.DEFAULT_ORDERING)
        return res

    def gen_paste(self):
        return SqlPaste()

    def save_paste(self, p):
        session = self._gen_session()
        session.save_or_update(p)
        session.commit()

    def setup_tables(self):
        metadata.create_all(self._engine)
