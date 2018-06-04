import sys
import json

import requests

from pprint import pprint


class SkyMesh:
    def __init__(self, baseurl='https://my.skymesh.net.au'):
        self._session = requests.Session()
        self._credentials_dict = {}
        self.baseurl = baseurl

    def login(self, username, password):
        user, realm = username.split('@')
        url = self.baseurl + '/services/myskymesh-login.jsonrpc'
        params = {"username":user,"realm":realm,"password":password}
        resp = self.rpc(url, 'myskymesh_realm_login_hashed', params)
        try:
            login_data = resp['result']['session']
            self._credentials_dict = dict(
                samsid = int(login_data['sams'][0]),
                type = login_data['types'][0],
                username = login_data['euser'],
                entityid = login_data['entityid'],
                hash = login_data['ehash']
            )
            logged_in = True
        except:
            logged_in = False
        return logged_in

    def rpc(self, url, method, params):
        params.update(self._credentials_dict)
        data = dict(method=method,
                    username="myskymesh", # always fixed?
                    vispid=1, # always fixed?
                    jsonrpc=2,
                    id=1, # could be any id (maps async req to response)
                    params=params)
        pprint(data)
        response = self._session.post(url, json=data)
#        pprint(response.request.headers.items())
#        pprint(response.request.body)
        print response.status_code, response.reason
        return json.loads(response.text)

    def site_down(self):
        url = self.baseurl + '/services/myskymesh-ipaddr.jsonrpc'
        resp = self.rpc(url, 'is_maint', {})
        is_down = False
        if resp['result']['is_maint']:
            is_down = True
        return is_down

    def get_usage(self):
        url = self.baseurl + '/services/tina-myskymesh.jsonrpc'
        resp = self.rpc(url, 'usage_table_daily2', {})
        return resp


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print 'USAGE: %s username password' % (sys.argv[0])
        print '  or'
        print 'USAGE: %s `cat credentials.txt`' % (sys.argv[0])
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    sm = SkyMesh()
    if sm.site_down():
        print "SKYMESH SITE UNDER MAINTAINANCE... TRY AGAIN LATER..."
        sys.exit()
    
    if not sm.login(username, password):
        print "LOGIN FAILED!"
        sys.exit()

    pprint(sm.get_usage())

#TINA STUFF OF INTEREST:
#  usage_this_month
#  daily_usage
#  usage_buckets
#  usage_last24hours





