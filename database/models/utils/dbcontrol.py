from typing import Dict, List
from database.models import createdb

database = createdb.DbCreator()
conn = database.conn
cursor = database.cursor


def insert_db(table: str, column_val: Dict):
    """Insert data to DB"""
    columns = ', '.join(column_val.keys())
    values = [tuple(map(str, column_val.values()))]
    placeholders = ", ".join("?" * len(column_val.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def update_db(table: str, filteredcolumn_val: Dict, column_val: Dict):
    """Updates data in db"""
    editable_column = ', '.join(column_val.keys())
    editable_value = ', '.join(column_val.values())
    filter_column = list(filteredcolumn_val.keys())[0]
    filter_value = filteredcolumn_val.get(filter_column)
    cursor.execute(
        f"UPDATE {table.lower()} "
        f"SET {editable_column} = ? "
        f"WHERE {filter_column} = ?;",
        (editable_value, filter_value))
    conn.commit()


def fetch(table: str, columns: List[str]) -> List[Dict]:
    """Get selected columns from DB"""
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table.lower()}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(table: str, column_val: Dict):
    """Delete data by ID from DB"""
    column = list(column_val.keys())[0]
    val = list(column_val.values())[0]
    cursor.execute(f"DELETE FROM {table} WHERE {column}='{val}'")
    conn.commit()


def clean_table(table: str):
    """Clean all data from table (table itself not remove)"""
    cursor.execute(
        f"TRUNCATE TABLE {table};"
    )
    conn.commit()


def sort(table: str, columns: List[str], filtr: str, order: str = 'DESC') -> List[Dict]:
    """Sort data by column (ASC or DSC)"""
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table.lower()} ORDER BY {filtr} {order}")
    rows = cursor.fetch()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def get_cursor():
    return cursor


def _init_db_():
    """Initialise DB"""
    db_creator = createdb.DbCreator()
    db_creator.__init_db__()


def check_table_empty(table: str) -> bool:
    """Check table is empty or not"""
    cursor.execute(f"SELECT CASE WHEN EXISTS (SELECT * FROM {table} LIMIT 1) THEN 0 ELSE 1 END")
    if cursor.fetchone()[0]:
        return True


_init_db_()
