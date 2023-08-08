import exceptions
from db.modelss.utilites import dbcontrol
from typing import Dict, List
from app_types import WebData, DbData
from config.db_config import WEBDATA_TABLE, DBDATA_TABLE

SQL_DATA_TYPES = {WebData: WEBDATA_TABLE, DbData: DBDATA_TABLE}


def db_write_data(data: WebData | DbData) -> None:
    """Writes data to SQL"""
    if type(data) not in SQL_DATA_TYPES:
        raise exceptions.NotSupportedDataType
    table = SQL_DATA_TYPES.get(type(data))
    dbcontrol.insert_db(table=table, column_val=data.__dict__)


def db_read_user_data(user: str) -> Dict:
    db_data = dbcontrol.fetch(table=WEBDATA_TABLE, columns=[each for each in WebData.__annotations__])
    demand_data = {}
    for each in db_data:
        if each.get('user') != user:
            continue
        demand_data[each.get('question')] = each.get('action')
    return demand_data


def db_read_data(table: str) -> List[Dict]:
    for key, value in SQL_DATA_TYPES.items():
        if value == table:
            data_type = key
            return dbcontrol.fetch(table=table, columns=[each for each in data_type.__annotations__])
    raise exceptions.NotSupportedDataType


def db_del_user_data(user: str) -> None:
    dbcontrol.delete(table=WEBDATA_TABLE, column_val={'user': user})

# def db_write_post_data(user_data: Dict):
#     """Write post schedule and text to DB"""
#     dbcontrol.insert_db(POSTS_TABLE, user_data)
#     vars_global.update_schedule[0] = True
#
#
# def db_read_post_data() -> List[Dict]:
#     """Read data from post table"""
#     data_columns = ['id', 'post_photo_id', 'post_text', 'schedule_period', 'schedule_time']
#     table_data = dbcontrol.fetch(POSTS_TABLE, data_columns)
#     return table_data
#
#
# def db_del_post_data(post_id: int):
#     data = {'id': post_id}
#     dbcontrol.delete(POSTS_TABLE, data)
#     vars_global.update_schedule[0] = True


