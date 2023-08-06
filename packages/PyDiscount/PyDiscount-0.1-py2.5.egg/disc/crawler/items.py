# -*- coding:utf-8 -*-

'''
Created on 2009-4-29

@author: mingqi
'''

import simplejson as json
from disc.sip.sipproxy import SIPTaobaoProxy
from disc import sip
from disc.sip.sipproxy import SIPError
from disc.crawler import dbsource
from disc import commutil

logger = commutil.get_logger("disc.crawl.items")

class Item:
    """ 
        iid
        title
        nick
        pic_path
        cid
        price
    """
    
class User:
    """
        nick
        score
        level
        good_num
        total_nums
    """
    
def crawl_items(cid, page_no, page_size ):
    logger.debug("crawling items cid=%s, page_no=%d, page_size=%d" %(cid, page_no, page_size))
    _proxy = SIPTaobaoProxy( sip.APP_CODE,sip.APP_SECRET )
    _res = _proxy.call_sip("taobao.items.get", 
                           fields = "iid,title,nick,pic_path,cid,price",
                           order_by = "delist_time:asc",
                           page_no = str(page_no),
                           page_size = str(page_size),
                           cid = cid
                           )
    _json_res = json.loads(_res)
    _result = []
    
    if( _json_res['rsp'].has_key('items') ):
        for _item_dict in _json_res['rsp']['items']:
            logger.debug("item iid=%(iid)s" % _item_dict)
            _item = Item()
            _item.iid = _item_dict['iid']
            _item.title = _item_dict['title']
            _item.nick = _item_dict['nick']
            if _item_dict.has_key('pic_path'):
                _item.pic_path = _item_dict['pic_path']
            else:
                _item.pic_path = None
            
            _item.cid = _item_dict['cid']
            _item.price = float(_item_dict['price'])
            
            _result.append(_item)
            
    return _result

def crawl_user(nicks):
    _proxy = SIPTaobaoProxy(sip.APP_CODE,sip.APP_SECRET)
    
    _nicks = []
    if isinstance(nicks, list) or isinstance(nicks, tuple):
        _nicks = list(nick)
        is_list = True
    else:
        _nicks.append(nicks)
        is_list = False

    _res = _proxy.call_sip("taobao.users.get", 
                           fields = "nick,seller_credit",
                           nicks = ",".join(_nicks)
                           )
    
    _json_res = json.loads(_res)
    
    _result = {}
    if _json_res['rsp'].has_key('users'):
        for _user_dict in _json_res['rsp']['users']:
            _user = User()
            _user.nick = _user_dict['nick']
            
            _seller_credit_dict = _user_dict['seller_credit']
            _user.score = int(_seller_credit_dict['score'])
            _user.level = int(_seller_credit_dict['level'])
            _user.good_num = int(_seller_credit_dict['good_num'])
            _user.total_num = int(_seller_credit_dict['total_num'])
            
            _result[_user.nick] = _user
            
    if not is_list:
        return _result[nicks]
    
    return _result
    
def sql_update_item(item):
    _update_sql = """ 
            update TB_ITEMS set
                CATEGORY_ID = %(cid)s,
                NICKNAME = %(nick)s,
                PRICE = %(price)s,
                TITLE = %(title)s,
                PIC_PATH = %(pic_path)s
            where ITEM_ID=%(iid)s
    """

    _insert_sql = """ 
            insert into TB_ITEMS(
                ITEM_ID,
                CATEGORY_ID,
                NICKNAME,
                PRICE,
                TITLE,
                PIC_PATH)
            values(
                %(iid)s,
                %(cid)s,
                %(nick)s,
                %(price)s,
                %(title)s,
                %(pic_path)s
            )
    """
    
    _conn = dbsource.get_conn()
    _cursor = _conn.cursor()
    _cursor.execute(_update_sql, vars(item) )
    if _cursor.rowcount == 0:
        _cursor.execute(_insert_sql, vars(item))
        
    return True

if __name__ == '__main__':
    _max_page_no = 100
    _page_size = 40

    _cid_list = ('1801',)
    
    
    for _cid in _cid_list:
        for _page_no in range(1, _max_page_no + 1):
            _item_list = crawl_items( _cid, _page_no, _page_size )
            
            # If no item be crawled, means page size have been overflowed
            if len(_item_list) == 0: break
            for _item in _item_list:
                if crawl_user(_item.nick).level <6:
                    continue
                sql_update_item(_item)
                logger.info("Update or Create Item %s:%s" % (_item.iid, _item.title) )