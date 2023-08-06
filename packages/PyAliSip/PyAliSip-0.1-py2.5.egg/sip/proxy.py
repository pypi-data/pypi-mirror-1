# coding:utf-8

'''
Created on 2009-5-3

@author: mingqi
'''

from datetime import datetime
from decorator import iter_fetch
from sip.sipclient import TaobaoSIPClient
import simplejson as json
import sip
from sip.sipclient import SIPError
import logging
logger = logging.getLogger('sip.proxy')

class SIPRespondeObj:
    '''
    wrap SIP's response. SIP's response is a dict. 
    By this class, we can access to attribute by 
    class attribute style(a.xxx) as well as dict style (a.['xxxx'])
    '''
    def __init__(self, dict):
        self.__dict__ = dict
        
    def __getitem__(self, key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        raise KeyError(key)
    
    def __str__(self):
        return ",".join([ "=".join((str(_k),str(_v))) for _k,_v in self.__dict__.iteritems()])
        
    

class TaobaoProxy(object):
    '''
    The proxy of calling Tapbao SPI API
    '''

    def __init__(self):
        self.__sip_client = TaobaoSIPClient(sip.APP_CODE, sip.APP_SECRET)

    def fetch_categories(self, cids=None, parent_cid=None, 
                         datetime= datetime.strptime('1970-01-01 00:00:00',"%Y-%m-%d %H:%M:%S")):
        '''
        Fetch the item category information.
        Input
            cids (optional): category id or list of category id 
            parent_id (optional): parent id.  If both of them absent, the datetime parameter
                should be required.
            datetime (optional): the last date time of category. It will be ignore if cid or parent_id present.
        Return a dict of category value:
            cid: category id
            parent_cid: parent category id
            is_parent
            name: category name
            status: 0 - normal 1 - deleted
            sort_order: the order of display in web site below same parent
            
        You also access to the item by key index ( [key] operator)
        '''
        _args = {'fields':'cid,parent_cid,is_parent,name,status,sort_order'}
        
        if cids:
            if isinstance(cids, str):
                _args['cids'] = cids
            else:
                _args['cids'] = ",".join(cids)
            
        if parent_cid:
            _args['parent_cid'] = parent_cid
            
        if not (cids or parent_cid):
            _args['datetime'] = datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        _json_res = json.loads(self.__sip_client.call_sip('taobao.itemcats.get.v2', **_args))
        _result = {}
        
        if not _json_res['rsp'].has_key('item_cats'):
            return None
        
        for _cat_dicts in _json_res['rsp']['item_cats']:
            if _cat_dicts['status'] == 'normal':
                _cat_dicts['status'] = 0
            elif _cat_dicts['status'] == 'deleted':
                _cat_dicts['status'] = 1
            
            _cat_dicts['sort_order'] = int(_cat_dicts['sort_order'])
            _cat_dicts['is_parent'] = bool(_cat_dicts['is_parent'])
            
            if _cat_dicts['cid'] != '0':
                _result[_cat_dicts['cid']] = SIPRespondeObj(_cat_dicts)
        
        return _result
        
    def fetch_properties(self, cid, parent_pid=None, pid=None):
        '''
        Fetch item's properties information by category.
        Input
            cid: category id
            parent_pid: parent property id
            pid: property id. parent_pid and pid are optional
        
        return a dict of item property, key is pid:
            pid
            name
            is_key_prop
            is_sale_prop
            is_color_prop
            is_enum_prop
            is_input_prop
            parent_pid
            parent_vid: parent property value id
            status: 0-normal 1-deleted
            sort_order
            
        if no corresponding properties, return a empty dict
        '''
        _args = {'fields':'pid,name,parent_pid,parent_vid, status,is_enum_prop,is_key_prop,is_sale_prop,is_color_prop,is_input_prop, sort_order'}
        _args['cid'] = cid
        _args['datetime'] = '2005-02-01 00:00:00'
        if parent_pid:
            _args['parent_pid'] = parent_pid
        
        if pid:
            _args['pid'] = pid
            
        
        _json_res = json.loads(self.__sip_client.call_sip('taobao.itemprops.get.v2', **_args))
        _result = {}
        
        if not _json_res['rsp'].has_key('item_props'):
            return None
        
        for _prop_dict in _json_res['rsp']['item_props']:
            for _prop_key in _prop_dict.iterkeys():
                if _prop_key.startswith('is_'):
                    _prop_dict[_prop_key] = bool(_prop_dict[_prop_key])
                if _prop_key == 'sort_order':
                    _prop_dict[_prop_key] = int(_prop_dict[_prop_key])
                if _prop_key == 'status':
                    if _prop_dict[_prop_key] == 'normal':
                        _prop_dict[_prop_key] = 0
                    elif _prop_dict[_prop_key] == 'deleted':
                        prop_dict[_prop_key] = 1
                    
            _result[_prop_dict['pid']] = SIPRespondeObj(_prop_dict)

        return _result
        
        
    def fetch_enums(self, cid):
        '''
        Fetch enum value of item property
        Input
           cid: category id
           
        Return a dict of enum valu:
            cid: category id
            pid: property id
            vid: enum value id
            name
            is_parent
            status 0-normal 1-deleted
            sort_order
        '''
        
        _args = {'cid':cid,
                 'fields':'cid,pid,prop_name,vid,name,is_parent,status,sort_order',
                 'datetime':'1970-1-1 00:00:00'}
        
        _json_res = json.loads(self.__sip_client.call_sip('taobao.itempropvalues.get', **_args))
        
        _result = {}
        if not _json_res['rsp'].has_key('prop_values'):
            return None
        
        for _enum_dict in _json_res['rsp']['prop_values']:
            if _enum_dict['status'] == 'normal':
                _enum_dict['status'] = 0
            elif _enum_dict['status'] == 'deleted':
                _enum_dict['status'] = 1
            
            _enum_dict['sort_order'] = int(_enum_dict['sort_order'])
            _result[_enum_dict['vid']] = SIPRespondeObj(_enum_dict)
            
        return _result

    
    def fetch_items_by_category(self, cid, order_by=None, page_no=1, page_size=40, with_props=False):
        '''
        Fetch items by category.
        Input
            cid: category id
            order_by: column:asc/desc. The column should be price, delist_time or seller_credit.
            page_size
            page_no
        return a iterator of items collect:
            iid
            price
            title
            nick
            props
            pic_path
        '''
        
        _args = {'cid':cid,
                 'page_no':str(page_no),
                 'page_size':str(page_size)}
        _args['fields'] = 'iid, price, title, nick, pic_path'
        _json_res = json.loads(self.__sip_client.call_sip('taobao.items.get', **_args))
        
        _result = []
        if not _json_res['rsp'].has_key('items'):
            return None
        for _item_dict in _json_res['rsp']['items']:
            _item_dict['price'] = float(_item_dict['price'])
            if with_props:
                _item_dict['props'] = self.get_item(_item_dict['nick'],_item_dict['iid']).props
            if not _item_dict.has_key('pic_path'):
                _item_dict['pic_path'] = None
            _result.append(SIPRespondeObj(_item_dict))
            
        return _result
        
        
    def get_item(self, nick,iid):
        '''
        get item information by item id
        return item information
            iid
            cid
            price
            title
            nick
            pic_path
            props: a list of properties            
        '''
        _args = {'iid':iid,
                 'nick':nick,
                 'fields':'iid,cid,price,title,nick,pic_path,props'}
        try:
            _json_res = json.loads(self.__sip_client.call_sip('taobao.item.get', **_args))
        except SIPError, e:
            if e.error_code == 551:
                return None
            raise e
        if not _json_res['rsp'].has_key('items'):
            return None
        if len(_json_res['rsp']['items'])==0:
            return None
        
        _item_dict = _json_res['rsp']['items'][0]
        _item_dict['price'] = float(_item_dict['price'])
        
        if _item_dict.has_key('props'):
            if len(_item_dict['props'])==0:
                a = {}
            a = dict([pair.split(':') for pair in _item_dict['props'].split(';')])
            _item_dict['props'] = a
                
        return SIPRespondeObj(_item_dict)
    
    def fetch_users(self, nicks):
        '''
        fetch user information
        Input:
            nicks: a nick or nick list
            
        Return a nick information or dict which key is nick name and value is nick information:
            nick
            score
            level
            good_num
            total_nums
        '''
        logger.debug('fetch_users, %s' % nicks)
        
        _args = {'fields':'nick,seller_credit'}
        if isinstance(nicks, basestring):
            _args['nicks'] = nicks
        else:
            _args['nicks'] = ",".join(nicks)
                
        
        _json_res = json.loads(self.__sip_client.call_sip('taobao.users.get',**_args))
        
        if not _json_res['rsp'].has_key('users'):
            return None
        
        _result = {}
        for _user_dict in _json_res['rsp']['users']:
            _credit_dict = _user_dict['seller_credit']
            _credit_dict['good_num'] = int(_credit_dict['good_num'])
            _credit_dict['level'] = int(_credit_dict['level'])
            _credit_dict['score'] = int(_credit_dict['score'])
            _credit_dict['total_num'] = int(_credit_dict['total_num'])
            
            _user_dict.update(_credit_dict)
            
            _result[_user_dict['nick']] = SIPRespondeObj(_user_dict)
            
        return _result
        
    def fetch_public_trans(self, nick, iid, page_no=1, page_size=40):
        '''
        Fetch public transaction data.
        Input
            nick: merchant nick name
            iid: item id
            
        Return a list of transaction information
            seller_nick
            buyer_nick
            iid
            price
            created
            num
        '''
        _args = {'iid':iid, 'seller_nick':nick,'page_no':str(page_no),'page_size':str(page_size)}
        _args['fields'] = 'seller_nick,buyer_nick,iid,price,num,created'
        
        _json_res = json.loads(self.__sip_client.call_sip('taobao.orders.get', **_args))
        
        if not _json_res['rsp'].has_key('orders'):
            return None
        
        _result = []
        for _trades_dict in _json_res['rsp']['orders']:
            _trades_dict['price'] = float(_trades_dict['price'])
            _trades_dict['num'] = float(_trades_dict['num'])
            _trades_dict['created'] = datetime.strptime(_trades_dict['created'],"%Y-%m-%d %H:%M:%S")
            
            _result.append(SIPRespondeObj(_trades_dict))
            
        return _result
    
if __name__ == '__main__':
    try:
        from sip import proxy
        from sip.sipclient import SIPError
        __proxy = proxy.TaobaoProxy()
        import sys
        logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG
                    )
        _users_dict = __proxy.fetch_public_trans('柠檬绿茶','943f600a76ee393628af834c3fa28daf')
        for _trade in _users_dict:
            print '%(created)s, %(buyer_nick)s, %(price)f' % vars(_trade) 
    except SIPError, e:
        print "error_status=%s, error_msg=%s" % (e.error_code,e.error_message)
#    for _user in _users_dict.iterkeys():
#        print repr(_user)
    
