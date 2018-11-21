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

TOKEN_URL = "https://account.api.here.com/oauth2/token"
API_SERVICE = "https://api-lookup.data.api.platform.here.com"

def load_config():
    return yaml.load(io.open("config.yaml", "r"))

def save_config(config):
    with io.open("config.yaml", "w") as yaml_file:
        yaml_file.write(unicode(yaml.dump(config, default_flow_style=False)))

def generate_access_token():
    config = load_config()
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

def get_access_token():
    config = load_config()
    if not "access_token" in config:
        access_token = generate_access_token()
        config["access_token"] = access_token
        save_config(config)
    return config["access_token"]

def add_bearer_token(headers):
    result = headers.copy()
    result.update({ "Authorization": "Bearer " + get_access_token() })
    return result

def api_get(url, headers=dict(), **kwargs):
    return requests.get(url, headers=add_bearer_token(headers), **kwargs)

pp = pprint.PrettyPrinter(indent=4)
res = api_get(API_SERVICE + "/lookup/v1/platform/apis")
pp.pprint(res)
pp.pprint(res.json())

