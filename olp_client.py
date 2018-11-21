#!/usr/bin/env python

import time
import os
import hmac
import requests
import hashlib
import urllib
import pprint
import random
import string
import base64
import json
import yaml
import io

class API:

    def __init__(self, api):
        self.name = api[u'api']
        self.base_url = api[u'baseURL']

    def __str__(self):
        return "API<" + self.name + "@" + self.base_url + ">"

class Catalog:

    def __init__(self, olpclient, catalog):
        self.olpclient = olpclient
        self.href = catalog[u'href']
        self.hrn = catalog[u'hrn']
        self.title = catalog[u'title']
        self.type = catalog[u'type']
        self.apis = None

    def __str__(self):
        return "Catalog<" + self.title + ">"

    def get_apis(self):
        if self.apis is None:
            self.apis = []
            for service in self.olpclient.api_get(OLPClient.API_SERVICE + "/lookup/v1/resources/" + self.hrn + "/apis").json():
                self.apis.append(API(service))
        return self.apis

class OLPClient:

    TOKEN_URL = "https://account.api.here.com/oauth2/token"
    API_SERVICE = "https://api-lookup.data.api.platform.here.com"

    def __init__(self):
        self.apis = None
        self.access_token = None
        self.catalogs = None

    def load_config(self):
        return yaml.load(io.open("config.yaml", "r"))

    def save_config(self, config):
        with io.open("config.yaml", "w") as yaml_file:
            yaml_file.write(unicode(yaml.dump(config, default_flow_style=False)))

    def generate_access_token(self):
        config = self.load_config()
        nonce = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
        timestamp = str(int(time.time()))
        oauth_params = {
          "oauth_consumer_key": config["client_id"],
          "oauth_signature_method": "HMAC-SHA256",
          "oauth_timestamp": timestamp,
          "oauth_nonce": nonce,
          "oauth_version": "1.0"
        }
        body_params = {
          "grant_type": "client_credentials"
        }
        signature_params = oauth_params.items() + body_params.items()
        signature_params.sort(key=(lambda x: x[0]))
        signature_base_string = "POST&" + urllib.quote(TOKEN_URL, safe='') + "&" + urllib.quote("&".join(urllib.quote(x[0]) + "=" + urllib.quote(x[1]) for x in signature_params))
        print "SBS: " + signature_base_string
        signature = base64.b64encode(hmac.new(config["client_secret"] + "&", signature_base_string, hashlib.sha256).digest())
        print "Signature Base64: " + signature

        oauth_params.update({
          "oauth_signature": signature
        })

        # Include the signature in the headers
        headers = {
            'Authorization': 'OAuth ' + ",".join(x[0] + '="' + urllib.quote(x[1], safe='') + '"' for x in oauth_params.items()),
            'Content-Type': 'application/x-www-form-urlencoded' # Only for POST requests
        }

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(headers)

        # Now that your request is signed, you can initiate an API call
        print "Sending request"
        res = requests.post(TOKEN_URL, data="grant_type=client_credentials", headers=headers)

        pp.pprint(res)
        pp.pprint(res.json())
        return res.json()["access_token"]

    def get_access_token(self):
        if self.access_token is not None:
            return self.access_token
        config = self.load_config()
        if not "access_token" in config:
            access_token = self.generate_access_token()
            config["access_token"] = access_token
            self.save_config(config)
        self.access_token = config["access_token"]
        return config["access_token"]

    def add_bearer_token(self, headers):
        result = headers.copy()
        result.update({ "Authorization": "Bearer " + self.get_access_token(), "Cache-Control": "no-cache" })
        return result

    def api_get(self, url, headers=dict(), **kwargs):
        return requests.get(url, headers=self.add_bearer_token(headers), **kwargs)

    def get_config_url(self):
        return self.get_api("config").base_url

    def get_api(self, name):
        return [ a for a in self.get_apis() if a.name == name ][0]

    def get_apis(self):
        if self.apis is None:
            self.apis = []
            res = self.api_get(self.API_SERVICE + "/lookup/v1/platform/apis")
            for service in res.json():
                 self.apis.append(API(service))
        return self.apis

    def get_catalogs(self):
        if self.catalogs is None:
            self.catalogs = []
            for catalog in self.api_get(self.get_config_url() + "/catalogs").json()[u'results'][u'items']:
                self.catalogs.append(Catalog(self, catalog))
        return self.catalogs

pp = pprint.PrettyPrinter(indent=4)
olp = OLPClient()
print "Catalogs:"
for catalog in olp.get_catalogs():
    print catalog
for api in olp.get_catalogs()[0].get_apis():
    print api
