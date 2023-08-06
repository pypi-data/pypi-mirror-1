# -*- coding:utf-8 -*-

'''
Created on 2009-4-28

@author: mingqi
'''
from disc import commutil
from disc.crawler import dbsource
from disc import sip
from disc.sip.sipproxy import SIPTaobaoProxy
from datetime import datetime
import simplejson as json

logger = commutil.get_logger("disc.sip.itemcat")

class PropertyEnum:
    """
    cid
    pid
    vid
    name
    status
    sort_order
    """

def sql_all_leaf_categories():
    "fetch all leaf category"
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    _sql = """
        select category_id from tb_item_categories where is_parent=0 and status=0
    """
    
    _cursor.execute(_sql)
    
    _category_list = []
    _row = None
    while 1:
        _row = _cursor.fetchone()
        if not _row: break
        _category_list.append(_row[0])
        
    _cursor.close()
    return _category_list

def sql_check_timestramp(cid):
    _sql = """ 
        select last_crawl_date from tb_property_crawl_timestamp
        where category_id=%s
    """
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    _cursor.execute(_sql, cid)
    
    _row = _cursor.fetchone()
    _cursor.close()
    if _row:
        return _row[0]
    return None

def sql_update_enum(enum_list):
    _update_sql = """
        update TB_ENUM_VALUES set
            PROPERTY_ID=%(pid)s,
            CATEGORY_ID=%(cid)s,
            ENUM_VALUE_NAME=%(name)s,
            STATUS=%(status)s,
            SORT_ORDER=%(sort_order)s,
            LAST_UPDATE_DATE=now()
        where ENUM_VALUE_ID=%(vid)s
    """
    
    _insert_sql = """
        insert into TB_ENUM_VALUES(
            ENUM_VALUE_ID,
            PROPERTY_ID,
            CATEGORY_ID,
            ENUM_VALUE_NAME,
            STATUS,
            SORT_ORDER,
            CREATION_DATE,
            LAST_UPDATE_DATE)
        values(
            %(vid)s,
            %(pid)s,
            %(cid)s,
            %(name)s,
            %(status)s,
            %(sort_order)s,
            now(),
            now()
        )
    """
    
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    
    for _enum in enum_list:
        logger.info("pulled enum %s:%s" % (_enum.vid, _enum.name))
        _cursor.execute(_update_sql, vars(_enum))
        if _cursor.rowcount == 0:
            _cursor.execute(_insert_sql, vars(_enum))
            
    return True

def post_timestamp(cid, timestamp):
    _update_sql = "update TB_ENUM_CRAWL_TIMESTAMP set LAST_CRAWL_DATE=%(timestamp)s where CATEGORY_ID=%(cid)s"
    _insert_sql = "insert into TB_ENUM_CRAWL_TIMESTAMP(CATEGORY_ID,LAST_CRAWL_DATE) values(%(cid)s,%(timestamp)s)"
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    _cursor.execute(_update_sql, vars())
    if _cursor.rowcount == 0:
        _cursor.execute(_insert_sql, vars() )
        
    return True

def crawl_enum_values(cid):
    "crawl enum values by category"
    
    _proxy = SIPTaobaoProxy(sip.APP_CODE,sip.APP_SECRET)
    _args = {"fields": "cid,pid,vid,name,is_parent,status,sort_order",
             "cid": str(cid)}
    
    _timestamp = sql_check_timestramp(cid)
    if _timestamp:
        _args["datetime"] = _timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else:
        _args["datetime"] = "1970-01-01 00:00:00"
        
    _res = _proxy.call_sip("taobao.itempropvalues.get", **_args)
    _json_res = json.loads(_res)
    
    _enum_list = []
    
    if _json_res['rsp'].has_key("prop_values"):
        for _enum_dict in _json_res['rsp']['prop_values']:
            _o = PropertyEnum()
            _o.cid = _enum_dict["cid"]
            _o.pid = _enum_dict["pid"]
            _o.vid = _enum_dict["vid"]
            _o.name = _enum_dict["name"]
            if _enum_dict["status"]=="normal":
                _o.status = 0
            else:
                _o.status = 1
            _o.sort_order = int(_enum_dict['sort_order'])
            _enum_list.append(_o)
            
    return _enum_list
            
if __name__ == '__main__':
    for _category_id in sql_all_leaf_categories():
        sql_update_enum(crawl_enum_values(_category_id))
        post_timestamp(_category_id, datetime.now())
        