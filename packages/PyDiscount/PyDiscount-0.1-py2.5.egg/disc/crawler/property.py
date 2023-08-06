# -*- coding:utf-8 -*-
'''
Created on 2009-4-25

@author: mingqi
'''

from disc import commutil
from disc.crawler import dbsource
from disc import sip
from disc.sip.sipproxy import SIPTaobaoProxy
from datetime import datetime
import simplejson as json

logger = commutil.get_logger("disc.sip.itemcat")

class ItemProperty:
    """
    pid
    name
    parent_pid
    parent_vid
    status
    is_key
    is_sale
    is_color
    is_enum
    is_input
    sort_order
    """

def get_leaf_categories():
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

def get_timestamp(cid):
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

def update_properties(property_list):
    _update_sql = """ update tb_properties set
            name = %(name)s,
            PARENT_PROPERTY_ID = %(parent_pid)s,
            PARENT_VALUE_ID = %(parent_vid)s,
            IS_KEY = %(is_key)s,
            IS_SALE = %(is_sale)s,
            IS_INPUT = %(is_input)s,
            IS_ENUM = %(is_enum)s,
            IS_COLOR = %(is_color)s,
            STATUS = %(status)s,
            SORT_ORDER = %(sort_order)s,
            LAST_UPDATE_DATE = now()
        where PROPERTY_ID=%(pid)s
    """
    
    _insert_sql = """ insert into tb_properties(
                        PROPERTY_ID,
                        name,
                        PARENT_PROPERTY_ID,
                        PARENT_VALUE_ID,
                        IS_KEY,
                        IS_SALE,
                        IS_INPUT,
                        IS_ENUM,
                        IS_COLOR,
                        STATUS,
                        SORT_ORDER,
                        CREATION_DATE,
                        LAST_UPDATE_DATE
                    ) values(
                        %(pid)s,
                        %(name)s,
                        %(parent_pid)s,
                        %(parent_vid)s,
                        %(is_key)s,
                        %(is_sale)s,
                        %(is_input)s,
                        %(is_enum)s,
                        %(is_color)s,
                        %(status)s,
                        %(sort_order)s,
                        now(),
                        now()
                    )"""
    
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    
    for _property in property_list:
        logger.info("scraped property %s: %s" % (_property.pid, _property.name))
        _cursor.execute(_update_sql, vars(_property))
        if _cursor.rowcount == 0:
            _cursor.execute(_insert_sql, vars(_property))
    
#    _cursor.close()
#    _conn.commit()
    return True
  
def post_timestamp(cid, timestamp):
    _update_sql = "update TB_PROPERTY_CRAWL_TIMESTAMP set LAST_CRAWL_DATE=%(timestamp)s where CATEGORY_ID=%(cid)s"
    _insert_sql = "insert into TB_PROPERTY_CRAWL_TIMESTAMP(CATEGORY_ID,LAST_CRAWL_DATE) values(%(cid)s,%(timestamp)s)"
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    _cursor.execute(_update_sql, vars())
    if _cursor.rowcount == 0:
        _cursor.execute(_insert_sql, vars() )
        
    return True
    

def crawl_properties(cid, parent_pid = None):
#    logger.debug("crawl properties cid:%s parent_pid:%s" % (cid, parent_pid))
    _proxy = SIPTaobaoProxy(sip.APP_CODE,sip.APP_SECRET)
    _args = {"fields": "pid,name,parent_pid,parent_vid,status,\
                        is_enum_prop, is_key_prop,\
                        is_sale_prop,is_color_prop,\
                        is_input_prop,sort_order",
             "cid": str(cid)}
    
    _timestamp = get_timestamp(cid)
#    logger.debug(_timestamp.__class__)
    if _timestamp:
        _args["datetime"] = _timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else:
        _args["datetime"] = "1970-01-01 00:00:00"
        
    if parent_pid:
        _args["parent_pid"] = str(parent_pid)
        
    _res = _proxy.call_sip("taobao.itemprops.get.v2", **_args)
    _json_res = json.loads(_res)
    
    _property_list = []
    if _json_res['rsp'].has_key("item_props"):
        for _prop_dict in _json_res['rsp']['item_props']:
            _o = ItemProperty()
            _o.pid = _prop_dict["pid"]
            _o.name = _prop_dict["name"]
            _o.is_key = bool(_prop_dict["is_key_prop"])
            _o.is_sale = bool(_prop_dict["is_sale_prop"])
            _o.is_color = bool(_prop_dict["is_color_prop"])
            _o.is_enum = bool(_prop_dict["is_enum_prop"])
            _o.is_input = bool(_prop_dict["is_input_prop"])
            if _prop_dict['status'] == "normal":
                _o.status = 0
            else:
                _o.status = 1
            _o.sort_order = int(_prop_dict['sort_order'])
            if _prop_dict["parent_pid"] == "0":
                _o.parent_pid = None
            else:
                _o.parent_pid = _prop_dict["parent_pid"]
                
            if _prop_dict["parent_vid"] == "0":
                _o.parent_vid = None
            else:
                _o.parent_vid = _prop_dict["parent_vid"]
            
#            logger.info("crawled properties: %s, %s" % (_o.pid, _o.name))
            _property_list.append(_o)
#            _property_list = _property_list + crawl_properties(cid, _o.pid)
        
    return _property_list
        
            
if __name__ == '__main__':
#    for p in crawl_properties("110210"):
#        print p.pid +", "+p.name
    for category_id in get_leaf_categories():
        update_properties(crawl_properties(category_id))
        post_timestamp(category_id, datetime.now())