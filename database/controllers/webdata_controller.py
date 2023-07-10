from datetime import datetime
from database.models.utils import dbcontrol
from typing import Dict
from app_types import WebData
from config.db_config import WEBDATA_TABLE


def db_write_data(data: WebData) -> None:
    dbcontrol.insert_db(table=WEBDATA_TABLE, column_val=data.__dict__)


def db_read_user_data(user: str) -> Dict:
    db_data = dbcontrol.fetch(table=WEBDATA_TABLE, columns=[each for each in WebData.__annotations__])
    demand_data = {}
    for each in db_data:
        if each.get('user') != user:
            continue
        demand_data[each.get('question')] = each.get('action')
    return demand_data


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
