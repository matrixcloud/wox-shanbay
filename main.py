#coding=utf-8

import os
import requests
import webbrowser
import re
import time
from wox import Wox,WoxAPI
from urllib.parse import parse_qs

TOKEN_FILE = os.path.abspath('token')

CLIENT_ID = 'f98628beb07b12b149af'

SEARCH_API = 'https://api.shanbay.com/bdc/search/?word='
LEARNING_API = 'https://api.shanbay.com/bdc/learning/?access_token='
AUTHORIZE_API = 'https://api.shanbay.com/oauth2/authorize/'

class Shanbay(Wox):
    def request(self, url):
        #If user set the proxy, you should handle it.
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
            proxies = {
                "http":"http://{}:{}".format(self.proxy.get("server"),self.proxy.get("port")),
                "https":"http://{}:{}".format(self.proxy.get("server"),self.proxy.get("port"))}
            return requests.get(url,proxies = proxies)
        else:
            return requests.get(url)

    def query(self, key):
        if True == key.startswith('#'):
            params = key
            return [{
                "Title": '授权保存',
                "SubTitle": 'authorize',
                "IcoPath": "Images/logo.png",
                "JsonRPCAction": {
                    "method": "saveToken",
                    "parameters": [params],
                    "dontHideAfterAction": True
                }
            }]
        data = self.request(SEARCH_API + key).json()['data']
        defs = re.split('\n', data['definition'])
        results = []

        for i in defs:
           results.append({
                "Title": i,
                "SubTitle": data['content'],
                "IcoPath": "Images/logo.png",
                "JsonRPCAction": {
                    "method": "learn",
                    "parameters": [data['conent_id']],
                    "dontHideAfterAction": True
                }
            })

        return results

    def learn(self, wordId):
        if False == self.hasToken():
            self.authorize()
            return
        token = self.getToken()
        if not token:
            WoxAPI.show_msg('token失效', 'token expiresed')
            return
        payload = {'id': wordId}
        r = requests.post(LEARNING_API + token, data = payload)
        if r.json()['status_code'] == 0:
            WoxAPI.show_msg('已添加', 'already added')
        else:
            WoxAPI.show_msg('请检查token', 'pls check token file')

    def authorize(self):
        url = '%s?client_id=%s&response_type=token&state=123' % (AUTHORIZE_API, CLIENT_ID)
        webbrowser.open(url)
    
    def saveToken(self, text):
        token = text.replace('#', '')
        token = token + '&timestamp=' + str(int(time.time()))
        f = open(TOKEN_FILE, 'w')
        f.write(token)
        f.close()
        WoxAPI.show_msg('凭证已保存', 'saved')
    
    def getToken(self):
        f = open(TOKEN_FILE, 'r')
        token = f.read()
        f.close()
        dic = parse_qs(token)
        if int(dic['timestamp'][0]) + int(dic['expires_in'][0]) < int(time.time()):
            return ''
        return dic['access_token'][0]

    def hasToken(self):
        return os.path.isfile(TOKEN_FILE)

if __name__=='__main__':
    Shanbay()