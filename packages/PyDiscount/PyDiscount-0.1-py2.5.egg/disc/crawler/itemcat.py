# -*- coding:utf-8 -*-

'''
Created on 2009-4-19

@author: mingqi
'''
from datetime import datetime
from disc import sip
from disc.sip.sipproxy import SIPTaobaoProxy
import simplejson as json
from disc.crawler import dbsource
from disc import commutil

logger = commutil.get_logger("disc.sip.itemcat")

class ItemCategory:
    """
    Attributes:
        cid
        parent_cid: 0-no paremtn
        name
        is_parent: boolean
        status:[0:normal, 1:deleted]
        sort_order: int
    """
    
class TaobaoItemCatsResult:
    """
    Attributes:
        last_modified: datetime
        item_cats: ItemCategory[]
    """

def crawl_item_cats(from_date=datetime.strptime('2008-01-01 00:00:00','%Y-%m-%d %H:%M:%S')):
    _proxy = SIPTaobaoProxy(sip.APP_CODE,sip.APP_SECRET)
    _res = _proxy.call_sip("taobao.itemcats.get.v2", 
                           fields = "cid,parent_cid,is_parent,name,status,sort_order",
                           datetime = from_date.strftime("%Y-%m-%d %H:%M:%S")
                           )
    _json_res = json.loads(_res)
    
    _result = TaobaoItemCatsResult()
    _result.last_modified = datetime.strptime(_json_res['rsp']['lastModified'],'%Y-%m-%d %H:%M:%S')
    _result.item_cats = []
    for _cat in _json_res['rsp']['item_cats']:
        _o = TaobaoItemCatsResult()
        _o.cid = _cat["cid"]
        _parent_id = int(_cat['parent_cid'])
        _o.parent_cid = _parent_id or None
        _o.name = _cat["name"]
        _o.is_parent = bool(_cat["is_parent"])
        _o.sort_order = _cat['sort_order']
        if _cat['status'] == "normal":
            _o.status = 0
        else:
            _o.status = 1
        
        _result.item_cats.append(_o)
    
    return _result

def insert_item_cat(item_cat):
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    _sql = """
        insert into tb_item_categories(
            CATEGORY_ID,
            NAME,
            IS_PARENT,
            PARENT_CATEGORY_ID,
            STATUS,
            SORT_ORDER,
            CREATION_DATE,
            LAST_UPDATE_DATE)
        values(
            %(cid)s,
            %(name)s,
            %(is_parent)s,
            %(parent_cid)s,
            %(status)s,
            %(sort_order)s,
            now(),
            now()
        )
        """  
    _cursor.execute(_sql, vars(item_cat))
    
    if _cursor.rowcount == 1:
        return True
    return False

def is_exists(cid):
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    _sql = """
        select count(*) from tb_item_categories where category_id=%s
        """
        
    _cursor.execute(_sql, cid)
    _count = _cursor.fetchone()[0]
    return (_count > 0)

def update_item_cat(item_cat):
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    _sql = """
        update tb_item_categories set
            NAME=%(name)s,
            IS_PARENT=%(is_parent)s,
            PARENT_CATEGORY_ID=%(parent_cid)s,
            STATUS=%(status)s,
            SORT_ORDER=%(sort_order)s,
            LAST_UPDATE_DATE=now()
        where CATEGORY_ID=%(cid)s
        """
    _cursor.execute(_sql, vars(item_cat) )
    
    if _cursor.rowcount == 0:
        return insert_item_cat(item_cat)
        
    return True

if __name__ == '__main__':
    _res = crawl_item_cats()
    
    logger.debug("Total category is %d" % len(_res.item_cats))
    for _item_cat in _res.item_cats:
        update_item_cat(_item_cat)
    
    print "success to update item's categories data"
