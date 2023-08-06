'''
Created on 2009-4-16

@author: mingqi
'''

import urllib
from disc import commutil
import md5
import datetime
from xml.etree import ElementTree 
import simplejson as json
 

logger = commutil.get_logger("disc.sip.sipproxy")

class SIPError(Exception):
    def __init__(self, error_status, error_message):
        self.__error_status = error_status
        self.__error_message = error_message
        
    def get_status(self):
        return self.__error_status
    
    def get_message(self):
        return self.__error_message
    
class SIPTaobaoBizError(SIPError):
    pass

class SIPProxy:
    
    def __init__(self, app_key, app_secret):
        self.__app_key = app_key
        self.__app_secret = app_secret
    
    def call_sip(self, api_name, sid=None, **args):
        sip_args = {}
        sip_args["sip_appkey"] = self.__app_key
        sip_args["sip_apiname"] = api_name
        sip_args["sip_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sip_args["sip_format"] = "json"
        
        if(sid):
            sip_args["sip_sessionid"] = sid
        
        sip_args.update(args)
        
        sign = self.__app_secret
        for key in sorted(sip_args):
            sign = sign + key + sip_args[key]
            
        sign = md5.new(sign).hexdigest()
        sip_args['sip_sign']=sign
        
        url = "http://sip.alisoft.com/sip/rest?"
        url = url + urllib.urlencode(sip_args)
        opener = urllib.urlopen(url)
        if not opener:
           raise SIPError(-1, "Connect to SIP errors")
        
        sip_status = int(opener.info().getheader('sip_status'))
        if sip_status != 9999:
            raise SIPError(sip_status, opener.info().getheader('sip_error_message'))
        
        return opener.read()

class SIPTaobaoProxy(SIPProxy):
    
    def call_sip(self, api_name, sid=None, **args):
        _args = {}
        _args.update(args)
        _args["v"] = "1.0"
        _args["format"] = "json"
        
        _res = SIPProxy.call_sip(self, api_name, **_args)
        _json_res = json.loads(_res)
        
        if _json_res.has_key("error_rsp"):
            _error_code = int(_json_res['error_rsp']['code'])
            _error_msg = _json_res['error_rsp']['msg']
            
            if _error_code < 500:
                raise SIPError(_error_code, _error_msg)
            
            raise SIPTaobaoBizError(_error_code, _error_msg)
        
        return _res
    
if __name__ == '__main__':
    try:
        _proxy = SIPTaobaoProxy("15665","c8c7cde08c9b11dd8d048c81fce5951d")
        _res = _proxy.call_sip("taobao.itemcats.get.v2", 
                               fields = "cid,name",
                               datetime = '2008-01-01 00:00:00'
                               )
#        print _res
    except SIPError, ins:
        print ins.get_status()
        print ins.get_message()
        
    print "finished"
        
    