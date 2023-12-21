from sqlalchemy import Column, DATE, ARRAY, Float, String, inspect, Table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()


class PostgresDB:
    def __init__(self, *, db_user: str, db_pass: str, db_host: str, db_port: int, db_name: str):
        database_url = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
        self._engine = create_engine(database_url, echo=False)
        self._session_maker = sessionmaker(bind=self._engine)

        self._user_table = Table('users', Base.metadata,
                                 Column('email', String(255), primary_key=True),
                                 Column('registered_at', DATE, nullable=False),
                                 Column('password', String(255), nullable=False),
                                 Column('min_intervals', ARRAY(Float), nullable=False),
                                 Column('max_intervals', ARRAY(Float), nullable=False),
                                 Column('min_holdings_time', ARRAY(Float), nullable=False),
                                 Column('max_holdings_time', ARRAY(Float), nullable=False))

        # Создаем таблицу только если её не существует
        inspector = inspect(self.engine)
        if not inspector.has_table(self.user_table.name):
            Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        session = self._session_maker()
        return session

    @property
    def engine(self):
        return self._engine

    @property
    def user_table(self):
        return self._user_table