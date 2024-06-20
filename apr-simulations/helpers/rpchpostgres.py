from helpers.utils import Utils
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session


class RPChPostgres:
    def __init__(self):
        self.username = Utils.envvar("PG_USERNAME", str)
        self.password = Utils.envvar("PG_PASSWORD", str)
        self.host = Utils.envvar("PG_HOST", str)
        self.port = Utils.envvar("PG_PORT", int)
        self.database = Utils.envvar("PG_DATABASE", str)

        print(f"Setup connection to PostgreSQL database on {self.host} as `{self.username}`")

        self.url = URL(
            drivername="postgresql+psycopg2",
            username=self.username,
            password=self.password,
            host=self.host,
            query={"sslmode": "require"},
            port=self.port,
            database=self.database,
        )

        self.engine = create_engine(self.url)
        self.session = Session(self.engine)

        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    def get_xday_data(self, table: str, days: int):
        table: Table = self.metadata.tables[table]
        # get all data from the last days including the row index
        select_stmt = table.select().where(table.c.created_at >= Utils.daysInThePast(days)).order_by(table.c.id.desc())
        requests = self.session.execute(select_stmt).fetchall()

        print(f"\tfetched data from `{table}`")    
        
        return requests
    
    def get_7day_data(self, table: str):
        return self.get_xday_data(table, 7)
    
    def get_30day_data(self, table: str):
        return self.get_xday_data(table, 30)

    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.engine.dispose()