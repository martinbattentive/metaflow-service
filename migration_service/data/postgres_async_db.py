import time
import os
import aiopg


class PostgresUtils(object):
    @staticmethod
    async def is_present(table_name):
        with (await AsyncPostgresDB.get_instance().pool.cursor()) as cur:
            await cur.execute(
                "select * from information_schema.tables where table_name=%s",
                (table_name,),
            )
            return bool(cur.rowcount)

class AsyncPostgresDB(object):
    connection = None
    __instance = None

    pool = None

    @staticmethod
    def get_instance():
        if AsyncPostgresDB.__instance is None:
            AsyncPostgresDB()
        return AsyncPostgresDB.__instance

    def __init__(self):
        if self.__instance is not None:
            return

        AsyncPostgresDB.__instance = self

    async def _init(self):

        host = os.environ.get("MF_METADATA_DB_HOST", "localhost").replace("'", "\'")
        port = os.environ.get("MF_METADATA_DB_PORT", 5432).replace("'", "\'")
        user = os.environ.get("MF_METADATA_DB_USER", "postgres").replace("'", "\'")
        password = os.environ.get("MF_METADATA_DB_PSWD", "postgres").replace("'", "\'")
        database_name = os.environ.get("MF_METADATA_DB_NAME", "postgres").replace("'", "\'")

        dsn = "dbname={0} user={1} password={2} host={3} port={4}".format(
            database_name, user, password, host, port
        )
        # todo make poolsize min and max configurable as well as timeout
        # todo add retry and better error message
        retries = 3
        for i in range(retries):
            while True:
                try:
                    self.pool = await aiopg.create_pool(dsn)
                except Exception as e:
                    if retries - i < 1:
                        raise e
                    time.sleep(1)
                    continue
                break
