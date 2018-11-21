#!/usr/bin/env python

import time, os, hmac, requests, hashlib, urllib, pprint, random, string, base64
token_url = "https://account.api.here.com/oauth2/token"
#token_url = "http://prospero.talkingcode.co.uk/token"
nonce = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
timestamp = str(int(time.time()))
client_id = "uxK617r3ewJXlZmxyia0RA"
#client_id = "abc123"
client_secret = "yTkhc9jMuplpTH6AZwXtBv7kpNbqQCQoLozmZz_WF4REkK6_xRWntoli4MDfhSnGFeA6XdSDtJ9wSLymv-xDag"
#client_secret = "def456"
oauth_params = {
  "oauth_consumer_key": client_id,
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
signature_base_string = "POST&" + urllib.quote(token_url, safe='') + "&" + urllib.quote("&".join(urllib.quote(x[0]) + "=" + urllib.quote(x[1]) for x in signature_params))
print "SBS: " + signature_base_string
signature = base64.b64encode(hmac.new(client_secret + "&", signature_base_string, hashlib.sha256).digest())
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
res = requests.post(token_url, data="grant_type=client_credentials", headers=headers)

pp.pprint(res)
print res.content
#
#from requests_oauthlib import OAuth2Session
#from oauthlib.oauth2 import BackendApplicationClient
#
#print "hello"
#
#client_id = "uxK617r3ewJXlZmxyia0RA"
#client = BackendApplicationClient(client_id=client_id)
#oauth = OAuth2Session(client=client)
#token = oauth.fetch_token(token_url='https://account.api.here.com/oauth2/token', client_id=client_id, client_secret='yTkhc9jMuplpTH6AZwXtBv7kpNbqQCQoLozmZz_WF4REkK6_xRWntoli4MDfhSnGFeA6XdSDtJ9wSLymv-xDag')
#
#print token
