import sqlite3
from dataclasses import dataclass
from app_types import BugQuestions, WebData

from config.db_config import DB_PATH, WEBDATA_TABLE


class DbCreator:
    """Creates database tables"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def _create_table(self, table_name: str, user_dataclass) -> None:
        """Creates table from given dataclass and table name"""
        db_data_format = convert_class_to_db_annotation(user_dataclass)
        db_data_format_string = ','.join([f'{key} {value}' for key, value in db_data_format.items()])
        with self.conn:
            self.cursor.execute(f"""CREATE TABLE {table_name} (
                                                id integer PRIMARY KEY,
                                                {db_data_format_string}
                                                )""")

    def __init_db__(self) -> None:
        tables = {WEBDATA_TABLE: WebData}
        for key, value in tables.items():
            try:
                self._create_table(table_name=key, user_dataclass=value)
            except sqlite3.OperationalError:
                pass


def convert_class_to_db_annotation(data_class: dataclass):
    """Converts python data types to SQLlite data types"""
    sqlite_types_relation = {str: 'text', int: 'integer'}
    db_data = {}
    for key, value in data_class.__annotations__.items():
        if value not in sqlite_types_relation:
            raise SyntaxError('Dataclass argument dont have corresponding type in SQLite')
        db_data[key] = sqlite_types_relation.get(value)
    return db_data
